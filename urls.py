# Copyright 2009 Luke Stone

from django.conf.urls.defaults import *

urlpatterns = patterns(
    'views',
    (r'^$', 'Welcome'),
    (r'^logout', 'LogOut'),
    (r'^room/', include('room.urls')),                      
    (r'^test', include('gaeunit.urls')),
)
