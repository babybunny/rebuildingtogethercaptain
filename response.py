# Copyright 2009 Luke Stone

"""Common codes for handling a response."""

import os

from google.appengine.api import users

import django
from django import shortcuts

HELP_CONTACT = 'al@rebuildingtogetherpeninsula.org'


def Respond(request, user, template_name, params=None):
  """Helper to render a response, passing standard stuff to the response.

  Args:
    request: The request object.
    user: The User object representing the current user; or None if nobody
      is logged in.
    template_name: The template name; '.html' is appended automatically.
    params: A dict giving the template parameters; modified in-place.

  Returns:
    Whatever render_to_response(template_name, params) returns.

  Raises:
    Whatever render_to_response(template_name, params) raises.
  """
  if user is None:
    user = users.GetCurrentUser()
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
