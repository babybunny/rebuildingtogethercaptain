"""Functional tests for WSGI app for Protocol RPC service API."""

import unittest
from webtest import TestApp

import app_engine_test_utils
from gae.room import choices_api
from test import test_models

app = TestApp(choices_api.application)


class ChoicesTest(unittest.TestCase):
  def setUp(self):
    app_engine_test_utils.activate_app_engine_testbed_and_clear_cache()
    self.keys = test_models.CreateAll()

  def tearDown(self):
    test_models.DeleteAll(self.keys)

  def testCaptainBadAuth(self):
    post_json_body = {}
    response = app.post_json('/choices_api.captain_choices_read',
                             post_json_body,
                             status=400,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.capn@gmail.com'})
    self.assertEquals('400 Bad Request', response.status)

  def testCaptain(self):

    post_json_body = {}
    response = app.post_json('/choices_api.captain_choices_read',
                             post_json_body,
                             status=200,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('200 OK', response.status)
    self.assertIn(u'choice', response.json)
    self.assertEquals(2, len(response.json['choice']))
    self.assertDictContainsSubset({u'label': u'Miss Captain'},
                                  response.json['choice'][0])

  def testCaptainForSite(self):
    post_json_body = {
          "id": self.keys['SITE'].integer_id(),
    }
    response = app.post_json('/choices_api.captain_for_site_choices_read',
                             post_json_body,
                             status=200,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.capn@gmail.com'})
    self.assertEquals('200 OK', response.status)
    self.assertIn(u'choice', response.json)
    self.assertEquals(1, len(response.json['choice']))
    self.assertDictContainsSubset({u'label': u'Miss Captain'},
                                  response.json['choice'][0])

  def testStaffposition(self):
    post_json_body = {}
    response = app.post_json('/choices_api.staffposition_choices_read',
                             post_json_body,
                             status=200,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('200 OK', response.status)
    self.assertIn(u'choice', response.json)
    self.assertEquals(3, len(response.json['choice']))
    self.assertDictContainsSubset({u'label': u'position one'},
                                  response.json['choice'][0])

  def testJurisdiction(self):
    post_json_body = {}
    response = app.post_json('/choices_api.jurisdiction_choices_read',
                             post_json_body,
                             status=200,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('200 OK', response.status)
    self.assertIn(u'choice', response.json)
    self.assertEquals(2, len(response.json['choice']))
    self.assertDictContainsSubset({u'label': u'FunkyTown'},
                                  response.json['choice'][0])

  def testOrdersheet(self):
    post_json_body = {}
    response = app.post_json('/choices_api.ordersheet_choices_read',
                             post_json_body,
                             status=200,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('200 OK', response.status)
    self.assertIn(u'choice', response.json)
    self.assertEquals(5, len(response.json['choice']))
    self.assertDictContainsSubset({u'label': u'Debris Box'},
                                  response.json['choice'][0])

  def testSupplier(self):
    post_json_body = {}
    response = app.post_json('/choices_api.supplier_choices_read',
                             post_json_body,
                             status=200,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('200 OK', response.status)
    self.assertIn(u'choice', response.json)
    self.assertEquals(2, len(response.json['choice']))
    self.assertDictContainsSubset({u'label': u'House of Supply'},
                                  response.json['choice'][0])  # this is stable because the choices are ordered.
