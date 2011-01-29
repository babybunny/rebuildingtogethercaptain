"""Methods common to all handlers."""

import os
from google.appengine.api import mail
from google.appengine.api import users
import django
from django import shortcuts
import models


# TODO: use rebuildingtogether.rooms@gmail.com ?
HELP_CONTACT = 'cari@rebuildingtogetherpeninsula.org'

# From: address of outbound emails.
EMAIL_SENDER = 'rebuildingtogether.rooms@gmail.com'
# CC'd on all emails as a logging mechanism.
EMAIL_LOG = 'rebuildingtogethercaptain@googlegroups.com'


def NotifyAdminViaMail(subject, text_body=None, html_body=None):
  message = mail.EmailMessage(sender=EMAIL_SENDER)
  message.subject = subject
  message.to = EMAIL_LOG
  if text_body is not None:
    message.body = text_body
  if html_body is not None:
    message.html = html_body
  message.send()


def GetBaseUri():
    if os.environ.get('SERVER_SOFTWARE', '').startswith('Development'):
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


