#!/usr/bin/env python
# Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Use Django 1.0 instead of the default.
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
# This seems to be a problem.
# from google.appengine.dist import use_library
# use_library('django', '1.0')

from appengine_django import InstallAppengineHelperForDjango
InstallAppengineHelperForDjango()

from captains import bootstrap_data

from django.core.management import execute_manager
try:
  import settings  # Assumed to be in the same directory.
except ImportError:
  import sys
  sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
  sys.exit(1)


if __name__ == "__main__":
  execute_manager(settings)
