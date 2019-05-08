"""Functional tests for staffposition API."""

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

  def testStaffpositionCreate(self):
    post_json_body = {"position_name": "Test Position"}
    response = app.post_json('/staffposition_api.staffposition_create', post_json_body, status=200,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('200 OK', response.status)

  def testStaffpositionCreateNoPositionName(self):
    post_json_body = {}
    response = app.post_json('/staffposition_api.staffposition_create', post_json_body, status=400,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('400 Bad Request', response.status)
    self.assertRaises('position name is required')

  def testStaffpositionRead(self):
    post_json_body = {"id": self.keys['STAFFPOSITION'].integer_id()}
    response = app.post_json('/staffposition_api.staffposition_read', post_json_body, status=200,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})

    self.assertEqual(u'position one', response.json[u'position_name'])
    self.assertEqual([{u'date': u'2016-01-01', u'rate': 0.54}], response.json[u'mileage_rates'])
    self.assertEqual('200 OK', response.status)
    self.assertNotIn(u'hourly_rates', response.json)

  def testStaffpositionReadNoId(self):
    post_json_body = {}
    response = app.post_json('/staffposition_api.staffposition_read', post_json_body, status=400,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEqual('400 Bad Request', response.status)
    self.assertRaises('id is required')

  def testStaffpositionReadUserNotStaff(self):
    post_json_body = {"id": self.keys['STAFFPOSITION'].integer_id()}
    response = app.post_json('/staffposition_api.staffposition_read', post_json_body, status=400,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.capn@gmail.com'})
    self.assertEqual(response.status, '400 Bad Request')
    self.assertRaises('Must be staff to use this API.')
    self.assertRaises('APPLICATION_ERROR')

  def testStaffpositionUpdate(self):
    post_json_body = {"id": self.keys['STAFFPOSITION2'].integer_id(),
                      "position_name": "Better Position Name",
                      "hourly_rates": [{u'date': u'2016-01-01', u'rate': 14.00}],
                      "mileage_rates": [{u'date': u'2016-01-01', u'rate': 0.54}]}
    response = app.post_json('/staffposition_api.staffposition_update', post_json_body, status=200,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('200 OK', response.status)

  def testStaffpositionUpdateNoDateInRates(self):
    post_json_body = {"id": self.keys['STAFFPOSITION2'].integer_id(),
                      "position_name": "Better Position Name",
                      "hourly_rates": [{u'date': u'', u'rate': 14.00}]}
    response = app.post_json('/staffposition_api.staffposition_update', post_json_body, status=400,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('400 Bad Request', response.status)
    self.assertRaises('Validation Error: Missing Date')
    self.assertRaises('APPLICATION_ERROR')

  def testStaffpositionUpdateNoRateInRates(self):
    post_json_body = {"id": self.keys['STAFFPOSITION2'].integer_id(),
                      "position_name": "Better Position Name",
                      "mileage_rates": [{u'date': u'2016-01-01', u'rate': 0}]}
    response = app.post_json('/staffposition_api.staffposition_update', post_json_body, status=200,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('200 OK', response.status)
    self.assertRaises('Validation Error: Missing Rate')
    self.assertRaises('APPLICATION_ERROR')


if __name__ == '__main__':
  unittest.main()

