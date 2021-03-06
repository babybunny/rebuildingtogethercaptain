"""Functional tests that create scenarios from multiple API calls.

These tests can mimic call patterns that are expected from the client.
For example, a set-then-get pattern.
"""

import unittest

from webtest import TestApp

import app_engine_test_utils
from gae.room import custom_api
from gae.room import cru_api
from test import test_models

app = TestApp(custom_api.application)
cru_app = TestApp(cru_api.application)

class ApiScenarioTest(unittest.TestCase):
  def setUp(self):
    app_engine_test_utils.activate_app_engine_testbed_and_clear_cache()

    self.keys = test_models.CreateAll()

  def tearDown(self):
    test_models.DeleteAll(self.keys)


  def testOrderFullCreateAndReadBack(self):
    post_json_body = {
      "order": {
        "site": str(self.keys['SITE'].integer_id()),
        "order_sheet": self.keys['ORDERSHEET'].integer_id()
      },
      "order_items": [
        {"item": self.keys['ITEM'].integer_id(), "quantity": "2"},
        {"item": self.keys['ITEM2'].integer_id(), "quantity": "0"},
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
    self.assertDictContainsSubset({u'item': self.keys['ITEM'].integer_id(),
                                   u'quantity': 2.0, u'unit_cost': 9.99},
                                  response.json['order_items'][0])
    self.assertIn(u'delivery', response.json)
    self.assertEquals(u'Person Man', response.json['delivery']['contact'])
    self.assertNotIn(u'retrieval', response.json)
    self.assertNotIn(u'pickup', response.json)
    self.assertNotIn(u'borrow', response.json)

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
         "quantity": "0"},
        {"item": self.keys['ITEM2'].integer_id(),
         "order": self.keys['ORDER2'].integer_id(),
         "quantity": "1"}
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
    self.assertEquals(4.99, response.json['order']['sub_total'])
    self.assertIn(u'order_sheet', response.json['order'])
    self.assertIn(u'order_items', response.json)
    self.assertEquals(1, len(response.json['order_items']))
    self.assertDictContainsSubset(
        {u"item": self.keys['ITEM2'].integer_id(),
         u"order": self.keys['ORDER2'].integer_id(),
         u"quantity": 1.0,
         u"unit_cost": 4.99}, response.json['order_items'][0])
    self.assertEquals(1, len(response.json['order_items']))
    self.assertIn(u'delivery', response.json)
    self.assertEquals(u'Person Man', response.json['delivery']['contact'])
    self.assertNotIn(u'retrieval', response.json)
    self.assertNotIn(u'pickup', response.json)
    self.assertNotIn(u'borrow', response.json)

  def testOrderFulfillThenChangeItemPrice(self):
    """Repro for issue #296

    Play with an order and see what happens to its sub_total when
    1) price changes before fulfillment
    2) price changes after fulfillment
    """
    order_id = self.keys['ORDER2'].integer_id()
    item_body = {
      "id": self.keys['ITEM'].integer_id(),
      "bar_code_number": 1234,
      "name": 'My First Item',
      "appears_on_order_form": self.keys['ORDERSHEET'].integer_id(),
      "order_form_section": 'The First Section',
      "description": """A Very nice item, very nice.  UPDATED""",
      "measure": 'Each',
      "unit_cost": 9.98,
      "supplier": self.keys['SUPPLIER'].integer_id(),
      "supplier_part_number": 'part1234',
      "url": 'http://example.com/item',
      "supports_extra_name_on_order": False,
    }
    
    # Just read the original value.  Should correspond to the sub_total in test_models.py.
    post_json_body = {"id": order_id}
    response = app.post_json('/custom_api.order_full_read',
                             post_json_body,
                             status=200,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals(19.98, response.json['order']['sub_total'])

    # Item is originally 9.99.  We will update to $10.00 each.
    post_json_body = dict(item_body)
    post_json_body['unit_cost'] = 10.00
    response = cru_app.post_json('/cru_api.item_update',
                             post_json_body,
                             status=200,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('200 OK', response.status)

    # Now the order should still be $19.98 because the order has not been saved since the item
    # price was changed.
    post_json_body = {"id": order_id};
    response = app.post_json('/custom_api.order_full_read',
                             post_json_body,
                             status=200,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals(19.98, response.json['order']['sub_total'])  

    # Change the order and we should get the new price.
    post_json_body = {
      "id": order_id,
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
    }
    response = app.post_json('/custom_api.order_full_update',
                             post_json_body,
                             status=200,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('200 OK', response.status)

    # Now we see the new price reflected, and the new quantity 10.00 * 4 = 40..
    post_json_body = {"id": order_id};
    response = app.post_json('/custom_api.order_full_read',
                             post_json_body,
                             status=200,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals(40.0, response.json['order']['sub_total'])

    # Fulfill should freeze the price.
    post_json_body = {"id": order_id}
    response = app.post_json('/custom_api.order_fulfill',
                             post_json_body,
                             status=200,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('200 OK', response.status)

    # Update to $11.  This should not change the order.
    post_json_body = dict(item_body)
    post_json_body['unit_cost'] = 11.00
    response = cru_app.post_json('/cru_api.item_update',
                             post_json_body,
                             status=200,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('200 OK', response.status)
    
    # Still $40 sub_total.
    post_json_body = {"id": order_id};
    response = app.post_json('/custom_api.order_full_read',
                             post_json_body,
                             status=200,
                             headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
    self.assertEquals('200 OK', response.status)
    self.assertIn(u'id', response.json)
    self.assertEquals(order_id, response.json['id'])
    self.assertIn(u'order', response.json)
    self.assertEquals(40.0, response.json['order']['sub_total'])

    # Make sure we are still dealing with the same OrderItem objects.
    oicls = test_models.ndb_models.OrderItem
    q = oicls.query(oicls.order == self.keys['ORDER2'])
    self.assertEquals(1, q.count())
    oi = q.get()
    self.assertEquals(self.keys['ORDER2'], oi.order)
    self.assertEquals(self.keys['ITEM'], oi.item)
