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

  def testOrderFormChoices(self):
    post_json_body = {}
    response = app.post_json('/custom_api.order_form_choices',
                             post_json_body,
                             status=200,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('200 OK', response.status)
    self.assertIn(u'order_form', response.json)
    self.assertEquals(5, len(response.json['order_form']))

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
    self.assertIn(u'id', response.json)

  def testOrderFullUpdate(self):
    post_json_body = {
      "id": self.keys['ORDER'].integer_id(),
      "order": {
        "site": str(self.keys['SITE'].integer_id()),
        "order_sheet": self.keys['ORDERSHEET'].integer_id()
      },
      "order_items": [
        {"item": self.keys['ITEM'].integer_id(),
         "order": self.keys['ORDER'].integer_id(),
         "quantity": "2"}
      ],
      "delivery": {
        "notes": "Please go around back.",
        "contact_phone": "650 555 1212",
        "contact": "Person Man",
        "delivery_date": "2017-09-27"
      }
    }
    response = app.post_json('/custom_api.order_full_update',
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

  def testOrderFullCreateAndReadBack(self):
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
    self.assertIn(u'id', response.json)
    order_id = response.json['id']
    
    post_json_body = {"id": order_id};
    response = app.post_json('/custom_api.order_full_read',
                             post_json_body,
                             status=200,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('200 OK', response.status)
    self.assertIn(u'id', response.json)
    self.assertEquals(order_id, response.json['id'])
    self.assertIn(u'order', response.json)
    self.assertIn(u'order_sheet', response.json['order'])
    self.assertIn(u'order_items', response.json)
    self.assertEquals(1, len(response.json['order_items']))
    self.assertIn(u'delivery', response.json)
    self.assertEquals(u'Person Man', response.json['delivery']['contact'])
    self.assertNotIn(u'retrieval', response.json)
    self.assertNotIn(u'pickup', response.json)

  def testOrderFullUpdateAndReadBack(self):
    post_json_body = {
      "id": self.keys['ORDER2'].integer_id(),
      "order": {
        "site": str(self.keys['SITE'].integer_id()),
        "order_sheet": self.keys['ORDERSHEET'].integer_id()
      },
      "order_items": [
        {"item": self.keys['ITEM'].integer_id(),
         "order": self.keys['ORDER2'].integer_id(),
         "id": self.keys['ORDERITEM21'].integer_id(),
         "quantity": "4"}
      ],
      "delivery": {
        "notes": "Please go around back.",
        "contact_phone": "650 555 1212",
        "contact": "Person Man",
        "delivery_date": "2017-09-27"
      }
    }
    response = app.post_json('/custom_api.order_full_update',
                             post_json_body,
                             status=200,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('200 OK', response.status)
    
    order_id = self.keys['ORDER2'].integer_id()
    post_json_body = {"id": order_id};
    response = app.post_json('/custom_api.order_full_read',
                             post_json_body,
                             status=200,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('200 OK', response.status)
    self.assertIn(u'id', response.json)
    self.assertEquals(order_id, response.json['id'])
    self.assertIn(u'order', response.json)
    self.assertIn(u'order_sheet', response.json['order'])
    self.assertIn(u'order_items', response.json)
    self.assertDictEqual(
        {u"item": self.keys['ITEM'].integer_id(),
         u"order": self.keys['ORDER2'].integer_id(),
         u"id": self.keys['ORDERITEM21'].integer_id(),
         u"quantity": 4.0}, response.json['order_items'][0])
    self.assertEquals(1, len(response.json['order_items']))
    self.assertIn(u'delivery', response.json)
    self.assertEquals(u'Person Man', response.json['delivery']['contact'])
    self.assertNotIn(u'retrieval', response.json)
    self.assertNotIn(u'pickup', response.json)

  def testOrderExisting(self):
    post_json_body = {
      "ordersheet_id": self.keys['ORDERSHEET'].integer_id(),
      "site_id": self.keys['SITE'].integer_id()};
    response = app.post_json('/custom_api.order_existing',
                             post_json_body,
                             status=200,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('200 OK', response.status)
    self.assertIn(u'order', response.json)
    self.assertEquals(2, len(response.json['order']))
    self.assertEquals(self.keys['ORDER'].integer_id(), response.json['order'][1]['id'])

  def testLogisticsDates(self):
    post_json_body = {"id": self.keys['SITE'].integer_id()};
    response = app.post_json('/custom_api.logistics_dates',
                             post_json_body,
                             status=200,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('200 OK', response.status)
    self.assertIn(u'logistics_date', response.json)
    self.assertEquals(5, len(response.json['logistics_date']))
    self.assertEquals(self.keys['ORDER'].integer_id(), response.json['logistics_date'][0]['order_id'])
    self.assertEquals('Apr 12', response.json['logistics_date'][0]['date'])
    self.assertEquals('Delivery', response.json['logistics_date'][0]['logistics_type'])
