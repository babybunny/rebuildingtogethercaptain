"""Functional tests for WSGI app for Protocol RPC service API."""

import unittest2
from webtest import TestApp
from room import wsgi_service
from test import test_models

app = TestApp(wsgi_service.application)

class RoomApiTest(unittest2.TestCase):
    def setUp(self):
        test_models.CreateAll()

    def testSupplierReadBadWrongMethod(self):
        response = app.get('/wsgi_service.supplier_read', status=400)
        self.assertEquals('400 Bad Request', response.status)

    def testSupplierReadBadNoContent(self):
        response = app.post_json('/wsgi_service.supplier_read', {}, status=400,
                                 headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
        self.assertEquals('400 Bad Request', response.status)

    def testSupplierReadBadWrongId(self):
        response = app.post_json('/wsgi_service.supplier_read',
                                 {'id': 999},
                                 status=400,
                                 headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
        self.assertEquals('400 Bad Request', response.status)

    def testSupplierReadOK(self):
        response = app.post_json('/wsgi_service.supplier_read',
                                 {'id': test_models.KEYS['SUPPLIER'].integer_id()},
                                 headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
        self.assertEquals('200 OK', response.status)
        self.assertIn('House of Supply', response)

    def testSupplierUpdateOK(self):
        response = app.post_json('/wsgi_service.supplier_update',
                                 {'id': test_models.KEYS['SUPPLIER'].integer_id(),
                                  'name': 'Home of Supply'},
                                 headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
        self.assertEquals('200 OK', response.status)
        self.assertIn('Home of Supply', response)
        
    def testSupplierUpdateBadMissingId(self):
        response = app.post_json('/wsgi_service.supplier_update',
                                 {'name': 'Hovel of Supply'},
                                 status=400,
                                 headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
        self.assertEquals('400 Bad Request', response.status)
        
    def testSupplierUpdateBadWrongId(self):
        response = app.post_json('/wsgi_service.supplier_update',
                                 {'id': 999,
                                  'name': 'Hovel of Supply'},
                                 status=400,
                                 headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
        self.assertEquals('400 Bad Request', response.status)
        
    def testSupplierCreateOK(self):
        response = app.post_json('/wsgi_service.supplier_create',
                                 {'name': 'Hovel of Supply'},
                                 headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
        self.assertEquals('200 OK', response.status)
        self.assertIn('Hovel of Supply', response)

    def testSupplierCreateBadHasId(self):
        response = app.post_json('/wsgi_service.supplier_create',
                                 {'id': test_models.KEYS['SUPPLIER'].integer_id(),
                                  'name': 'Hovel of Supply'},
                                 status=400,
                                 headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
        self.assertEquals('400 Bad Request', response.status)

        

def makeTestMethods(name, fields):
        
    def tstCreateOK(self):
        post_json_body = {}
        post_json_body.update(fields)
        response = app.post_json('/wsgi_service.{}_create'.format(name.lower()),
                                 post_json_body,
                                 headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
        self.assertEquals('200 OK', response.status)
        self.assertIn(post_json_body['name'], response)

    def tstCreateBadHasId(self):
        post_json_body = {'id': test_models.KEYS[name.upper()].integer_id()}
        post_json_body.update(fields)
        response = app.post_json('/wsgi_service.{}_create'.format(name.lower()),
                                 post_json_body,
                                 status=400,
                                 headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
        self.assertEquals('400 Bad Request', response.status)

    return tstCreateOK, tstCreateBadHasId


for name, fields in (
        ('Supplier', {'name': 'House'}),
        ('Staff', {'name': 'Stef Staff', 'email': 'steff@example.com'})):
    tstCreateOK, tstCreateBadHasId = makeTestMethods(name, fields)
    setattr(RoomApiTest, 'test{}GenericCreateOK'.format(name), tstCreateOK)
    setattr(RoomApiTest, 'test{}GenericCreateBadHasId'.format(name), tstCreateBadHasId)
