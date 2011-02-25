"""Methods common to all handlers."""

import os
import pprint
from google.appengine.api import mail
from google.appengine.api import users
import django
from django import shortcuts
from django.template import loader
import models

NRD = '04/24/2011'

# TODO: use rebuildingtogether.rooms@gmail.com ?
HELP_CONTACT = 'cari@rebuildingtogetherpeninsula.org'

# From: address of outbound emails.
EMAIL_SENDER = 'rebuildingtogether.rooms@gmail.com'
EMAIL_SENDER_READABLE = 'Rebuilding Together ROOMS Support'
# CC'd on all emails as a logging mechanism.
EMAIL_LOG = 'rebuildingtogethercaptain@googlegroups.com'


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
  message.send()


def SendMail(to, subject, text, template, template_dict):
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
  else:
    sender = '%s <%s>' % (EMAIL_SENDER_READABLE, EMAIL_SENDER)
  message.sender = sender
  message.subject = subject
  if is_dev:
    message.to = EMAIL_LOG
  else:
    message.to = to
  message.reply_to = EMAIL_LOG
  if text is not None:
    message.body = text
  if html is not None:
    message.html = html
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
  captain = models.Captain.all().filter('email = ', user.email()).get()
  user.captain = captain
  staff = models.Staff.all().filter('email = ', user.email()).get()  
  user.staff = staff
  return user, captain, staff


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
    params['is_admin'] = (users.IsCurrentUserAdmin() and
                          'Dev' in os.getenv('SERVER_SOFTWARE'))
  else:
    params['sign_in'] = users.CreateLoginURL(request.path)
  params['help_contact'] = HELP_CONTACT
  if not template_name.endswith('.html'):
    template_name += '.html'
  return shortcuts.render_to_response(template_name, params)


