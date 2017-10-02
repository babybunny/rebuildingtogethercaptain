"""Functional tests for WSGI app for Protocol RPC service API."""

import unittest

from webtest import TestApp

import app_engine_test_utils
from room import wsgi_service
from test import test_models

app = TestApp(wsgi_service.application)

# Configuration for basic CRUD tests.
# List of pairs: (model name, fields dict)
# Include required messages in fields.
models_and_data = (
    ('Jurisdiction', {'name': 'Smallville'}),
    ('Staff', {'name': 'Stef Staff', 'email': 'steff@example.com'}),
    ('Captain', {'name': 'Cary Captain', 'email': 'cary@example.com'}),
    ('Supplier', {'name': 'House'}),
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
        response = app.post_json('/wsgi_service.{}_create'.format(name.lower()),
                                 post_json_body,
                                 headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
        self.assertEquals('200 OK', response.status)
        self.assertIn(post_json_body['name'], response)

    def tstCreateBadHasId(self):
        post_json_body = {'id': self.keys[name.upper()].integer_id()}
        post_json_body.update(fields)
        response = app.post_json('/wsgi_service.{}_create'.format(name.lower()),
                                 post_json_body,
                                 status=400,
                                 headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
        self.assertEquals('400 Bad Request', response.status)

    def tstReadBadWrongMethod(self):
        response = app.get('/wsgi_service.{}_read'.format(name.lower()),
                           status=400)
        self.assertEquals('400 Bad Request', response.status)

    def tstReadBadNoContent(self):
        response = app.post_json('/wsgi_service.{}_read'.format(name.lower()),
                                 {},
                                 status=400,
                                 headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
        self.assertEquals('400 Bad Request', response.status)

    def tstReadBadWrongId(self):
        response = app.post_json('/wsgi_service.{}_read'.format(name.lower()),
                                 {'id': 999},
                                 status=400,
                                 headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
        self.assertEquals('400 Bad Request', response.status)

    def tstReadOK(self):
        response = app.post_json('/wsgi_service.{}_read'.format(name.lower()),
                                 {'id': self.keys[name.upper()].integer_id()},
                                 headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
        self.assertEquals('200 OK', response.status)
        self.assertIn('id', response)

    def tstUpdateOK(self):
        post_json_body = {'id': self.keys[name.upper()].integer_id()}
        post_json_body.update(fields)
        response = app.post_json('/wsgi_service.{}_update'.format(name.lower()),
                                 post_json_body,
                                 headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
        self.assertEquals('200 OK', response.status)
        self.assertIn('id', response)
        self.assertIn(fields.keys().pop(), response)

    def tstUpdateBadMissingId(self):
        post_json_body = {}
        post_json_body.update(fields)
        response = app.post_json('/wsgi_service.{}_update'.format(name.lower()),
                                 post_json_body,
                                 status=400,
                                 headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
        self.assertEquals('400 Bad Request', response.status)

    def tstUpdateBadWrongId(self):
        post_json_body = {'id': 999}
        post_json_body.update(fields)
        response = app.post_json('/wsgi_service.{}_update'.format(name.lower()),
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


class ChoicesTest(unittest.TestCase):
    def setUp(self):
        app_engine_test_utils.activate_app_engine_testbed_and_clear_cache()

        self.keys = test_models.CreateAll()

    def tearDown(self):
        test_models.DeleteAll(self.keys)

    def testSupplier(self):
        post_json_body = {}
        response = app.post_json('/wsgi_service.supplier_choices_read',
                                 post_json_body,
                                 status=200,
                                 headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
        self.assertEquals('200 OK', response.status)
        self.assertIn(u'choice', response.json)
        self.assertEquals(1, len(response.json['choice']))
        self.assertDictContainsSubset({u'label': u'House of Supply'}, response.json['choice'][0])


class BugsTest(unittest.TestCase):
    def setUp(self):
        app_engine_test_utils.activate_app_engine_testbed_and_clear_cache()

        self.keys = test_models.CreateAll()

    def tearDown(self):
        test_models.DeleteAll(self.keys)

    def testCheckRequest(self):
        post_json_body = {
            "site": self.keys['SITE'].integer_id(),
            "labor_amount": 45.67,
            "form_of_business": "Corporation",
            "description": "For Services Rendered",
            "address": "123 checkrequest street",
            "materials_amount": 23.45,
            "captain": self.keys['CAPTAIN'].integer_id(),
            "state": "submitted",
            "payment_date": "2011-02-03",
            "name": "Mister Payable",
            "tax_id": "123-456-8790",
            "food_amount": 12.34}
        response = app.post_json('/wsgi_service.checkrequest_create',

                                 post_json_body,
                                 status=200,
                                 headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
        self.assertEquals('200 OK', response.status)
        self.assertIn(u'payment_date', response.json)
        self.assertEquals('2011-02-03', response.json['payment_date'])

    def testCaptainNoEmail(self):
        post_json_body = {
            "name": "Mister Captain",
        }
        response = app.post_json('/wsgi_service.captain_create',
                                 post_json_body,
                                 status=200,
                                 headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
        self.assertEquals('200 OK', response.status)
        self.assertIn(u'name', response.json)
        self.assertEquals('Mister Captain', response.json['name'])

    def testCaptainEmptyEmail(self):
        post_json_body = {
            "name": "Mister Captain",
            "email": ""}
        response = app.post_json('/wsgi_service.captain_create',
                                 post_json_body,
                                 status=200,
                                 headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
        self.assertEquals('200 OK', response.status)
        self.assertIn(u'name', response.json)
        self.assertEquals('Mister Captain', response.json['name'])

    def testCaptainLowerEmail(self):
        post_json_body = {
            "name": "Mister Captain",
            "email": "Mister@Captain.com"}
        response = app.post_json('/wsgi_service.captain_create',
                                 post_json_body,
                                 status=200,
                                 headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
        self.assertEquals('200 OK', response.status)
        self.assertIn(u'email', response.json)
        self.assertEquals('mister@captain.com', response.json['email'])


class CustomApiTest(unittest.TestCase):
    def setUp(self):
        app_engine_test_utils.activate_app_engine_testbed_and_clear_cache()

        self.keys = test_models.CreateAll()

    def tearDown(self):
        test_models.DeleteAll(self.keys)

    def testOrderSheetDetails(self):
        post_json_body = {
            "id": self.keys['ORDERSHEET'].integer_id(),
        }
        response = app.post_json('/wsgi_service.order_form_detail',
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
        response = app.post_json('/wsgi_service.order_full_create',
                                 post_json_body,
                                 status=200,
                                 headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
        self.assertEquals('200 OK', response.status)

    def testOrderFullRead(self):
        post_json_body = {"id": self.keys['ORDER'].integer_id()};
        response = app.post_json('/wsgi_service.order_full_read',
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
