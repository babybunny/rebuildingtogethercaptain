"""Functional tests for WSGI app for Protocol RPC service API."""

import unittest

from webtest import TestApp

import app_engine_test_utils
from gae.room import cru_api
from test import test_models

app = TestApp(cru_api.application)

# Configuration for basic CRUD tests.
# List of pairs: (model name, fields dict)
# Include required messages in fields.
models_and_data = (
  # ('Jurisdiction', {'name': 'Smallville'}),
  # ('Staff', {'name': 'Stef Staff', 'email': 'steff@example.com'}),
  # ('Captain', {'name': 'Cary Captain', 'email': 'cary@example.com'}),
  # ('Supplier', {'name': 'House'}),
  ('StaffPosition', {'name': 'Test Position'}),
)


class BasicCrudTest(unittest.TestCase):
  def setUp(self):
    app_engine_test_utils.activate_app_engine_testbed_and_clear_cache()

    self.keys = test_models.CreateAll()

  def tearDown(self):
    test_models.DeleteAll(self.keys)


def makeTestMethods(name, fields):
  """Returns a list of generic test methods for CRUD operations."""

  def tstCreateOK(self):
    post_json_body = {}
    post_json_body.update(fields)
    response = app.post_json('/cru_api.{}_create'.format(name.lower()),
                             post_json_body,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('200 OK', response.status)
    self.assertIn(post_json_body['name'], response)

  def tstCreateBadHasId(self):
    post_json_body = {'id': self.keys[name.upper()].integer_id()}
    post_json_body.update(fields)
    response = app.post_json('/cru_api.{}_create'.format(name.lower()),
                             post_json_body,
                             status=400,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('400 Bad Request', response.status)

  def tstReadBadWrongMethod(self):
    response = app.get('/cru_api.{}_read'.format(name.lower()),
                       status=400)
    self.assertEquals('400 Bad Request', response.status)

  def tstReadBadNoContent(self):
    response = app.post_json('/cru_api.{}_read'.format(name.lower()),
                             {},
                             status=400,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('400 Bad Request', response.status)

  def tstReadBadWrongId(self):
    response = app.post_json('/cru_api.{}_read'.format(name.lower()),
                             {'id': 999},
                             status=400,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('400 Bad Request', response.status)

  def tstReadOK(self):
    response = app.post_json('/cru_api.{}_read'.format(name.lower()),
                             {'id': self.keys[name.upper()].integer_id()},
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('200 OK', response.status)
    self.assertIn('id', response)

  def tstUpdateOK(self):
    post_json_body = {'id': self.keys[name.upper()].integer_id()}
    post_json_body.update(fields)
    response = app.post_json('/cru_api.{}_update'.format(name.lower()),
                             post_json_body,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('200 OK', response.status)
    self.assertIn('id', response)
    self.assertIn(fields.keys().pop(), response)

  def tstUpdateBadMissingId(self):
    post_json_body = {}
    post_json_body.update(fields)
    response = app.post_json('/cru_api.{}_update'.format(name.lower()),
                             post_json_body,
                             status=400,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('400 Bad Request', response.status)

  def tstUpdateBadWrongId(self):
    post_json_body = {'id': 999}
    post_json_body.update(fields)
    response = app.post_json('/cru_api.{}_update'.format(name.lower()),
                             post_json_body,
                             status=400,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('400 Bad Request', response.status)

  return (tstCreateOK,
          tstCreateBadHasId,
          tstReadBadWrongMethod,
          tstReadBadNoContent,
          tstReadBadWrongId,
          tstReadOK,
          tstUpdateOK,
          tstUpdateBadMissingId,
          tstUpdateBadWrongId)


for name, fields in models_and_data:
  (tstCreateOK,
   tstCreateBadHasId,
   tstReadBadWrongMethod,
   tstReadBadNoContent,
   tstReadBadWrongId,
   tstReadOK,
   tstUpdateOK,
   tstUpdateBadMissingId,
   tstUpdateBadWrongId) = makeTestMethods(name, fields)
  setattr(BasicCrudTest, 'test{}CreateOK'.format(name), tstCreateOK)
  setattr(BasicCrudTest, 'test{}CreateBadHasId'.format(name), tstCreateBadHasId)
  setattr(BasicCrudTest, 'test{}ReadBadWrongMethod'.format(name), tstReadBadWrongMethod)
  setattr(BasicCrudTest, 'test{}ReadBadNoContent'.format(name), tstReadBadNoContent)
  setattr(BasicCrudTest, 'test{}ReadBadWrongId'.format(name), tstReadBadWrongId)
  setattr(BasicCrudTest, 'test{}ReadOK'.format(name), tstReadOK)
  setattr(BasicCrudTest, 'test{}UpdateOK'.format(name), tstUpdateOK)
  setattr(BasicCrudTest, 'test{}UpdateBadMissingId'.format(name), tstUpdateBadMissingId)
  setattr(BasicCrudTest, 'test{}UpdateBadWrongId'.format(name), tstUpdateBadWrongId)


class BugsTest(unittest.TestCase):
  def setUp(self):
    app_engine_test_utils.activate_app_engine_testbed_and_clear_cache()

    self.keys = test_models.CreateAll()

  def tearDown(self):
    test_models.DeleteAll(self.keys)

  # def testCheckRequest(self):
  #   post_json_body = {
  #     "site": self.keys['SITE'].integer_id(),
  #     "labor_amount": 45.67,
  #     "form_of_business": "Corporation",
  #     "description": "For Services Rendered",
  #     "address": "123 checkrequest street",
  #     "materials_amount": 23.45,
  #     "captain": self.keys['CAPTAIN'].integer_id(),
  #     "state": "submitted",
  #     "payment_date": "2011-02-03",
  #     "name": "Mister Payable",
  #     "tax_id": "123-456-8790",
  #     "food_amount": 12.34}
  #   response = app.post_json('/cru_api.checkrequest_create',

  #                            post_json_body,
  #                            status=200,
  #                            headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
  #   self.assertEquals('200 OK', response.status)
  #   self.assertIn(u'payment_date', response.json)
  #   self.assertEquals('2011-02-03', response.json['payment_date'])

  # def testCaptainNoEmail(self):
  #   post_json_body = {
  #     "name": "Mister Captain",
  #   }
  #   response = app.post_json('/cru_api.captain_create',
  #                            post_json_body,
  #                            status=200,
  #                            headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
  #   self.assertEquals('200 OK', response.status)
  #   self.assertIn(u'name', response.json)
  #   self.assertEquals('Mister Captain', response.json['name'])

  # def testCaptainEmptyEmail(self):
  #   post_json_body = {
  #     "name": "Mister Captain",
  #     "email": ""}
  #   response = app.post_json('/cru_api.captain_create',
  #                            post_json_body,
  #                            status=200,
  #                            headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
  #   self.assertEquals('200 OK', response.status)
  #   self.assertIn(u'name', response.json)
  #   self.assertEquals('Mister Captain', response.json['name'])

  # def testCaptainLowerEmail(self):
  #   post_json_body = {
  #     "name": "Mister Captain",
  #     "email": "Mister@Captain.com"}
  #   response = app.post_json('/cru_api.captain_create',
  #                            post_json_body,
  #                            status=200,
  #                            headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
  #   self.assertEquals('200 OK', response.status)
  #   self.assertIn(u'email', response.json)
  #   self.assertEquals('mister@captain.com', response.json['email'])

  # def testSiteCaptainMissingType(self):
  #   post_json_body = {
  #     "site": self.keys['SITE'].integer_id(),
  #     "captain": self.keys['CAPTAIN'].integer_id(),
  #     }
  #   response = app.post_json('/cru_api.sitecaptain_create',
  #                            post_json_body,
  #                            status=400,
  #                            headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
  #   self.assertIn('type is required', response.body)

  # def testSiteCaptainDelete(self):
  #   post_json_body = {"id": self.keys['SITECAPTAIN'].integer_id()}
  #   response = app.post_json('/cru_api.sitecaptain_delete',
  #                            post_json_body,
  #                            status=200,
  #                            headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
  #   self.assertEquals('200 OK', response.status)
  #   self.assertIsNone(self.keys['SITECAPTAIN'].get())

  def testStaffPosition_MissingHourlyRateAfterDate(self):
    post_json_body = {"id": self.keys['STAFFPOSITION'].integer_id()}
    response = app.post_json('/cru_api.staffposition_read',
                             post_json_body,
                             status=200,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('200 OK', response.status)
    self.assertEquals(0.0, response.json['hourly_rate'])
    self.assertEquals(0.54, response.json['mileage_rate'])


  def testStaffPosition_Name(self):
    post_json_body = {"id": self.keys['STAFFPOSITION2'].integer_id()}
    response = app.post_json('/cru_api.staffposition_read',
                             post_json_body,
                             status=200,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('200 OK', response.status)
    self.assertNotIn(u'position_name', response.json)
    self.assertEquals("position two", response.json['name'])


  def testStaffPosition_IncludingHourlyAndMileageRateAfterDate(self):
    post_json_body = {"id": self.keys['STAFFPOSITION3'].integer_id()}
    response = app.post_json('/cru_api.staffposition_read',
                             post_json_body,
                             status=200,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('200 OK', response.status)
    self.assertNotIn(u'hourly_rate_after_date', response.json)
    self.assertNotIn(u'mileage_rate_after_date', response.json)
    self.assertEquals(20.00, response.json['hourly_rate'])
    self.assertEquals(0.58, response.json['mileage_rate'])

