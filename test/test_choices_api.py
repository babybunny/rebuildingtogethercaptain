"""Functional tests for WSGI app for Protocol RPC service API."""

import unittest

from webtest import TestApp

import app_engine_test_utils
from room import choices_api
from test import test_models

app = TestApp(choices_api.application)


class ChoicesTest(unittest.TestCase):
  def setUp(self):
    app_engine_test_utils.activate_app_engine_testbed_and_clear_cache()

    self.keys = test_models.CreateAll()

  def tearDown(self):
    test_models.DeleteAll(self.keys)

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
