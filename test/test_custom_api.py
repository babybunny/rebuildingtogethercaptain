"""Functional tests for WSGI app for Protocol RPC - custom API."""

import unittest

from webtest import TestApp

import app_engine_test_utils
from gae.room import custom_api
from test import test_models

app = TestApp(custom_api.application)

class CustomApiTest(unittest.TestCase):
  def setUp(self):
    app_engine_test_utils.activate_app_engine_testbed_and_clear_cache()

    self.keys = test_models.CreateAll()

  def tearDown(self):
    test_models.DeleteAll(self.keys)

  def testSiteCaptainDelete(self):
    post_json_body = {"id": self.keys['SITECAPTAIN'].integer_id()}
    response = app.post_json('/custom_api.sitecaptain_delete',
                             post_json_body,
                             status=200,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('200 OK', response.status)
    self.assertIsNone(self.keys['SITECAPTAIN'].get())

  def testOrderSheetDetails(self):
    post_json_body = {
      "id": self.keys['ORDERSHEET'].integer_id(),
    }
    response = app.post_json('/custom_api.order_form_detail',
                             post_json_body,
                             status=200,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('200 OK', response.status)
    self.assertIn(u'order_sheet', response.json)
    self.assertIn(u'sorted_items', response.json)
    # TODO: more checks

  def testOrderFullCreate(self):
    post_json_body = {
      "order": {
        "site": str(self.keys['SITE'].integer_id()),
        "order_sheet": self.keys['ORDERSHEET'].integer_id()
      },
      "order_items": [
        {"item": self.keys['ITEM'].integer_id(), "quantity": "2"}
      ],
      "delivery": {
        "notes": "Please go around back.",
        "contact_phone": "650 555 1212",
        "contact": "Person Man",
        "delivery_date": "2017-09-27"
      }
    }
    response = app.post_json('/custom_api.order_full_create',
                             post_json_body,
                             status=200,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('200 OK', response.status)

  def testOrderFullRead(self):
    post_json_body = {"id": self.keys['ORDER'].integer_id()};
    response = app.post_json('/custom_api.order_full_read',
                             post_json_body,
                             status=200,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('200 OK', response.status)
    self.assertIn(u'id', response.json)
    self.assertEquals(self.keys['ORDER'].integer_id(), response.json['id'])
    self.assertIn(u'order', response.json)
    self.assertIn(u'order_sheet', response.json['order'])
    self.assertIn(u'order_items', response.json)
    self.assertEquals(3, len(response.json['order_items']))
    self.assertIn(u'delivery', response.json)
    self.assertEquals(u'Joe Delivery', response.json['delivery']['contact'])
    self.assertIn(u'retrieval', response.json)
    self.assertEquals(u'Joe Retrieval', response.json['retrieval']['contact'])
    self.assertIn(u'pickup', response.json)
    self.assertEquals(u'Joe Pickup', response.json['pickup']['contact'])
