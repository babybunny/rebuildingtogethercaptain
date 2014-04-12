"""Methods common to all handlers."""

import os
import pprint
from google.appengine.api import mail
from google.appengine.api import users
import django
from django import shortcuts
from django.core import urlresolvers 
from django.template import loader
import models

# Current value of National Rebuilding Day!
# Used for various default values, for debris box pickup, eg.
# TODO: merge into PROGRAMS
NRD = '04/27/2014'

PROGRAMS = [
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

def NotifyAdminViaMail(subject, template, template_dict):
  base_uri = GetBaseUri()
  td = template_dict.copy()
  is_dev = IsDev()
  td['is_dev'] = is_dev
  td['base_uri'] = base_uri
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


def IsDev():
  return os.environ.get('SERVER_SOFTWARE', '').startswith('Development')


def GetBaseUri():
    if IsDev():
      return 'http://localhost:%s/' % os.environ.get('SERVER_PORT')
    return 'http://%s.appspot.com/' % os.environ.get('APPLICATION_ID')


def GetUser(request, user=None):
  if user is None:
    user = users.GetCurrentUser()
  captain = models.Captain.all().filter('email = ', user.email().lower()).get()
  user.captain = captain
  staff = models.Staff.all().filter('email = ', user.email().lower()).get()  
  user.staff = staff
  if user.staff:
    user.programs = PROGRAMS
    user.program_selected = staff.program_selected
  else:
    user.programs = []
    user.program_selected = None
  return user, captain, staff


def GetStaffCaptain():
  """Returns a Captain record which represents the RTP Staff."""
  return models.Captain.all().filter('email = ', STAFF_CAPTAIN_EMAIL).get()


def Respond(request, template_name, params=None):
  """Helper to render a response, passing standard stuff to the response.

  Args:
    request: The request object.
    template_name: The template name; '.html' is appended automatically.
    params: A dict giving the template parameters; modified in-place.

  Returns:
    Whatever render_to_response(template_name, params) returns.

  Raises:
    Whatever render_to_response(template_name, params) raises.
  """
  user, _, _ = GetUser(request)
  if params is None:
    params = {}
  if user:
    params['user'] = user
    params['sign_out'] = users.CreateLogoutURL('/')
    params['show_admin_link'] = (users.IsCurrentUserAdmin() and
                                 'Dev' in os.getenv('SERVER_SOFTWARE'))
    params['show_dashboard_link'] = (users.IsCurrentUserAdmin() and
                                     'Dev' not in os.getenv('SERVER_SOFTWARE'))
  else:
    params['sign_in'] = users.CreateLoginURL(request.path)
  params['help_contact'] = HELP_CONTACT
  params['help_phone'] = HELP_PHONE
  params['help_person'] = HELP_PERSON
  if not template_name.endswith('.html'):
    template_name += '.html'
  return shortcuts.render_to_response(template_name, params)

