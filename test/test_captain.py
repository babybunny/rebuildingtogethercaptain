"""Functional tests for captain views."""

import unittest

from webtest import TestApp
import app_engine_test_utils
from gae import main
from test import test_models

APP = TestApp(main.app)


class StatefulTestCaptain(unittest.TestCase):
  def setUp(self):
    self.testbed = app_engine_test_utils.activate_app_engine_testbed_and_clear_cache()

    self.keys = test_models.CreateAll()
    s = self.keys['CAPTAIN'].get()
    s.program_selected = '2011 TEST'
    s.put()

  def tearDown(self):
    test_models.DeleteAll(self.keys)
    self.testbed.deactivate()

  def _get(self, path):
    return APP.get(path, headers={'x-rooms-dev-signin-email': 'rebuildingtogether.capn@gmail.com'})

  def testCaptainHome(self):
    response = self._get('/room/captain_home')
    self.assertIn('Ahoy Captain!', response.body)

  def testCaptainHomeSites(self):
    response = self._get('/room/captain_home')
    self.assertNotIn(self.keys['SITE'].get().number.encode('ascii'), response.body)
    self.assertIn(self.keys['SITE2'].get().number.encode('ascii'), response.body)
