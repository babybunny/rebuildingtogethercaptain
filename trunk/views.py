# Copyright 2009 Luke Stone

"""Basic views for the entire RTP app."""

from google.appengine.api import users
import django
from django import http
from django import shortcuts
from room import views

def LogOut(request):
  r = http.HttpResponse('<h1>You have logged out.</h1>')
  return r

def Welcome(request):
  user = users.GetCurrentUser()
  home = views.FindHome(user, '/')
  if home != '/':
    return http.HttpResponseRedirect(home)

  # not logged in or no account set up.
  params = {}
  params['user'] = user
  return shortcuts.render_to_response('welcome.html', params)


  
    

