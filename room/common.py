"""Methods common to all handlers."""

import jinja2
import logging
import os
import pprint
import webapp2
from google.appengine.api import mail
from google.appengine.api import users
import ndb_models

# Current value of National Rebuilding Day!
# Used for various default values, for debris box pickup, eg.
# TODO: merge into PROGRAMS
NRD = '04/29/2017'

DEFAULT_CAPTAIN_PROGRAM = '2017 NRD'

PROGRAMS = [
    '2017 NRD',
    '2017 Safe',
    '2017 Teambuild',
    '2016 NRD',
    '2016 Misc',
    '2016 Safe',
    '2016 Energy',
    '2016 Teambuild',
    '2016 Youth',
    '2015 NRD',
    '2015 Misc',
    '2015 Safe',
    '2015 Energy',
    '2015 Teambuild',
    '2015 Youth',
    '2014 NRD',
    '2014 Misc',
    '2014 Safe',
    '2014 Energy',
    '2014 Teambuild',
    '2014 Youth',
    '2013 NRD',
    '2013 Misc',
    '2013 Safe',
    '2013 Energy',
    '2013 Teambuild',
    '2013 Youth',
    '2012 NRD',
    '2012 Misc',
    '2012 Safe',
    '2012 Energy',
    '2012 Teambuild',
    '2012 Youth',
    '2011 NRD',
    '2011 Misc',
    '2011 Safe',
    '2011 Energy',
    '2011 Teambuild',
    '2011 Youth',
    '2011 Test',
    '2010 NRD',
]

# TODO: use rebuildingtogether.rooms@gmail.com ?
HELP_CONTACT = 'cari@rebuildingtogetherpeninsula.org'
HELP_PERSON = 'Cari Pang Chen'
HELP_PHONE = '650-366-6597 x224'

# From: address of outbound emails.
EMAIL_SENDER = 'rebuildingtogether.rooms@gmail.com'
EMAIL_SENDER_READABLE = 'Rebuilding Together ROOMS Support'
# CC'd on all emails as a logging mechanism.
EMAIL_LOG = 'rebuildingtogethercaptain@googlegroups.com'
EMAIL_LOG_LINK = ('https://groups.google.com/forum/#!forum/'
                  'rebuildingtogethercaptain')
# Placeholder Captain record which represents RTP Staff.
STAFF_CAPTAIN_EMAIL = 'rebuildingtogether.rooms@gmail.com'

# for site views
MAP_WIDTH = 300
MAP_HEIGHT = 200

# CLEANUP this can probably be removed.
START_NEW_ORDER_SUBMIT = 'Start New Order'


def IsDev():
  return os.environ.get('SERVER_SOFTWARE', '').startswith('Development')


def GetUser(request):
  """Determines the current user and loads some state. 

  In production, gets user from appengine.api.users.get_current_user(). So,
  it should be used in App Engine handlers with login: required.

  Special handling for development server (dev_appserver.py): 

  First, try to get user from the request, expecting an email address as 
  the value of the X-ROOMS_DEV_SIGNIN_EMAIL header.

  Fall back to pre-configured identify from environment, meaning it was
  probably set in app.yaml or unit test initialization like nose2-gae config.

  Args:
    request: the current WSGI request. 

  Returns:
    user: appengine.api.users.User object, or None if user can not be determined
    status: string describing how user was determined, for logging and debugging
  """
  if not hasattr(request, 'registry'):
    request.registry = {}
  if 'user' in request.registry:
    return request.registry.get('user'), request.registry.get('status')

  user = users.get_current_user()
  if user and user.email():
    status = 'User from get_current_user %s' % user.email()
  else:
    status = 'User not available with users.get_current_user'

  if not user and IsDev():
    email = request.headers.get('X-ROOMS_DEV_SIGNIN_EMAIL')
    if email:
      status = 'DEV, using user from X-ROOMS_DEV_SIGNIN_EMAIL header %s' % email
    else:
      email = os.environ.get('ROOMS_DEV_SIGNIN_EMAIL')
      if email:
        status = 'DEV, using configured user from env var ROOMS_DEV_SIGNIN_EMAIL %s' % email

    if email:
      user = users.User(email=email)
      
  logging.info(status)

  if user and user.email():
    user.captain = ndb_models.Captain.query(
      ndb_models.Captain.email == user.email().lower()).get()
    user.staff = ndb_models.Staff.query(
      ndb_models.Staff.email == user.email().lower()).get()

    if user.staff:
      user.programs = PROGRAMS
      user.program_selected = user.staff.program_selected
    else:
      user.programs = []
      user.program_selected = None

  request.registry['user'], request.registry['status'] = user, status
  return user, status


# unused?
def GetStaffCaptain():
  """Returns a Captain record which represents the RTP Staff."""
  return models.Captain.all().filter('email = ', STAFF_CAPTAIN_EMAIL).get()



jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
      os.path.join(os.path.dirname(__file__), 'templates')))

def Respond(request_handler, template_name, params=None):
  """Helper to render a response, passing standard stuff to the response.
  Args:
    request_handler: The webapp2.RequestHandler instance that is handling this request.
        The request.registry dict is automatically added to params.
    template_name: The template name; '.html' is appended automatically.
    params: A dict giving the template parameters; modified in-place.
  Returns:
    webapp2.Response
  Raises:
    TODO
  """
  if params is None:
    params = {}
  params['webapp2'] = webapp2
  params['logout_url'] = users.create_logout_url('/')  
  params.update(request_handler.registry)
  params['help_contact'] = HELP_CONTACT
  params['help_phone'] = HELP_PHONE
  params['help_person'] = HELP_PERSON
  if not template_name.endswith('.html'):
    template_name += '.html'
  template = jinja_environment.get_template(template_name)
  request_handler.response.out.write(template.render(params))






import re
from jinja2 import evalcontextfilter, Markup, escape

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

@evalcontextfilter
def nl2br(eval_ctx, value):
  result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', Markup('<br>\n'))
                        for p in _paragraph_re.split(escape(value)))
  if eval_ctx.autoescape:
    result = Markup(result)
  return result


def GetBaseUri():
  if IsDev():
    return 'http://localhost:%s/' % os.environ.get('SERVER_PORT')
  return 'http://%s.appspot.com/' % os.environ.get('APPLICATION_ID')


def NotifyAdminViaMail(subject, template, template_dict):
  base_uri = GetBaseUri()
  td = template_dict.copy()
  is_dev = IsDev()
  td['is_dev'] = is_dev
  td['base_uri'] = base_uri

  # issue252.  this will crash until that's resolved.
  html = loader.render_to_string(template, td)
  text = pprint.pformat(td)
  message = mail.EmailMessage()
  # The "<Name> email" format of sender doesn't work with the dev server
  # because it shells out to a sendmail command with the arguments unquoted.
  if is_dev:
    sender = EMAIL_SENDER
  else:
    sender = '%s <%s>' % (EMAIL_SENDER_READABLE, EMAIL_SENDER)
  message.sender = sender
  message.subject = subject
  message.to = EMAIL_LOG
  message.reply_to = EMAIL_LOG
  if text is not None:
    message.body = text
  if html is not None:
    message.html = html
  message.check_initialized()
  message.send()


def SendMail(to, sender, cc, subject, text, template, template_dict):
  base_uri = GetBaseUri()
  td = template_dict.copy()
  is_dev = IsDev()
  td['is_dev'] = is_dev
  td['base_uri'] = base_uri
  html = loader.render_to_string(template, td)
  message = mail.EmailMessage()
  # The "<Name> email" format of sender doesn't work with the dev server
  # because it shells out to a sendmail command with the arguments unquoted.
  if is_dev:
    sender = EMAIL_SENDER
  message.sender = sender
  message.subject = subject
  ccs = [a.strip() for a in cc.split(',')] + [EMAIL_LOG]
  message.cc = [cc for cc in ccs if cc]
  if is_dev:
    message.to = EMAIL_LOG
  else:
    message.to = to
  if text is not None:
    message.body = text
  if html is not None:
    message.html = html
  message.check_initialized()
  message.send()

