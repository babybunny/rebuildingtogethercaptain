# Copyright 2009 Luke Stone

"""Basic views for the entire RTP app."""

import logging
from google.appengine.api import users
import django
from django import http
from django import shortcuts
from room import views

def Welcome(request):
  user = users.GetCurrentUser()
  home = views.FindHome(user, '/')
  if home != '/':
    return http.HttpResponseRedirect(home)

  # not logged in or no account set up.
  params = {}
  params['user'] = user
  params['logout_url'] = users.create_logout_url('/')
  return shortcuts.render_to_response('welcome.html', params)


  
    

