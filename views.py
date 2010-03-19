# Copyright 2009 Luke Stone

"""Basic views for the entire RTP app."""

import django
from django import http
from room import views

def LogOut(request):
  r = http.HttpResponse('<h1>You have logged out.</h1>')
  return r

def Welcome(request):
  return views.Welcome(request)

