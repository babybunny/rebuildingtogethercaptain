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
