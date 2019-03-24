"""Functional tests for WSGI app for Protocol RPC - staffposition API."""

import unittest

from webtest import TestApp

import app_engine_test_utils
from gae.room import staffposition_api
from test import test_models

app = TestApp(staffposition_api.application)

class StaffpositionApiTest(unittest.TestCase):
  def setUp(self):
    app_engine_test_utils.activate_app_engine_testbed_and_clear_cache()
    self.keys = test_models.CreateAll()

  def tearDown(self):
    test_models.DeleteAll(self.keys)

  def testStaffpositionRead(self):
    post_json_body = {"id": self.keys['STAFFPOSITION'].integer_id()};
    response = app.post_json('/staffposition_api.staffposition_read',
                             post_json_body,
                             status=200,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('200 OK', response.status)
    self.assertIn(u'position_name', response.json)
    self.assertIn(u'mileage_rates', response.json)
    self.assertNotIn(u'hourly_rates', response.json)
if __name__ == '__main__':
  unittest.main()
