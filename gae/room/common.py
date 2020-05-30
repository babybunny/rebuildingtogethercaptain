"""Methods common to all handlers."""

import os
import pprint

import jinja2
import webapp2
from google.appengine.api import mail
from google.appengine.api import users

import ndb_models
# Current value of National Rebuilding Day!
# Used for various default values, for debris box pickup, eg.
# TODO: merge into PROGRAMS
import issue147_program_as_model

NRD = '04/29/2017'


# TODO: use rebuildingtogether.rooms@gmail.com ?
HELP_CONTACT = 'greg@rebuildingtogetherpeninsula.org'
HELP_PERSON = 'Greg'
HELP_PHONE = '650-366-6597 x228'

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

class InvalidUserError(Exception):
  pass


class RoomsUser(object):

  DEV_EMAIL_ENVVAR = 'ROOMS_DEV_SIGNIN_EMAIL'

  @staticmethod
  def from_request(request):
    """
      Determines the current user and loads some state.

      In production, gets user from appengine.api.users.get_current_user(). So,
      it should be used in App Engine handlers with login: required.

      Special handling for development server (dev_appserver.py):

      First, try to get user from the request, expecting an email address as
      the value of the X-ROOMS_DEV_SIGNIN_EMAIL header.

      Fall back to pre-configured identify from environment, meaning it was
      probably set in app.yaml or unit test initialization like nose2-gae config.

    :param request: the current WSGI request.
    :type request: webapp2.Request
    :return: a RoomsUser, see above
    :rtype: RoomsUser
    """
    if not hasattr(request, 'registry'):
      request.registry = {}
    if 'user' in request.registry:
      user = request.registry.get('user')
      user.status = request.registry.get('status')
      return user

    try:
      user = RoomsUser()
      user.status = 'User from get_current_user %s' % user.email
    except users.UserNotFoundError:
      if IsDev():
        user = RoomsUser.get_dev_user(request)
      else:
        return None

    request.registry['user'], request.registry['status'] = user, user.status
    return user

  @staticmethod
  def get_dev_user(request):
    if type(request.headers) is list:
      headers = {k: v for (k, v) in request.headers}
    else:
      headers = request.headers

    email = headers.get('x-rooms-dev-signin-email')
    status = 'DEV, using user from x-rooms-dev-signin-email header %s' % email
    if not email:
      email = os.environ.get('ROOMS_DEV_SIGNIN_EMAIL')
      status = 'DEV, using configured user from env var ROOMS_DEV_SIGNIN_EMAIL %s' % email
      if not email:
        raise users.UserNotFoundError("Could not parse dev user from headers or environment variable")

    user = RoomsUser(provider=users.User, email=email)
    user.status = status
    return user

  def __init__(self, provider=users.User, *args, **kwargs):
    """
    encapsulates a user in the rooms system, usually a google.appengine.api.users.User with some added state
    but choosing non-inheritance pattern in order to provide flexibility going forward

    NOTE: We expect the provider object allows parameterless instantiation as well as with an email parameter

    :param provider: Object used to seed the user, default is google.appengine.api.users.User
    :type provider: object
    :param args and kwargs: arguments for provider constructor, eg email for google.appengine.api.users.User
    """
    assert callable(provider), "provider argument for {} should be callable".format(RoomsUser.__name__)
    self.provider = provider
    self.captain = None
    self.staff = None
    self.programs = []
    self.program_selected = None
    self.status = None
    self.email = None
    self.nickname = None
    self.provided_user = provider(*args, **kwargs)
    self._validate_provided_user_and_set_email()
    self._set_role_atributes()

  def _validate_provided_user_and_set_email(self):
    if self.provided_user is None:
      raise users.UserNotFoundError("provider {} returned None".format(self.provider))
    if not hasattr(self.provided_user, 'email'):
      raise InvalidUserError("Provided user {} does not have an email attribute".format(self.provided_user))
    email_attr = self.provided_user.email
    if callable(email_attr):
      self.email = email_attr()
    elif isinstance(email_attr, basestring):
      self.email = email_attr
    if not self.email or not isinstance(self.email, basestring):
      raise InvalidUserError("email attribute for provided user {} is invalid".format(self.provided_user))
    if not hasattr(self.provided_user, 'nickname'):
      raise InvalidUserError("Provided user {} does not have an nickname attribute".format(self.provided_user))
    self.nickname = self.provided_user.nickname
    if callable(self.nickname):
      self.nickname = self.nickname()

  def _set_role_atributes(self):
    self.captain = ndb_models.Captain.query(
      ndb_models.Captain.email == self.email.lower()).get()
    self.staff = ndb_models.Staff.query(
      ndb_models.Staff.email == self.email.lower()).get()
    if self.staff:
      self.programs = issue147_program_as_model.get_all_programs()
      self.program_selected = self.staff.program_selected


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
  if '.' not in template_name:
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
