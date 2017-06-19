"""Functional tests for WSGI app for Protocol RPC service API."""

import unittest2
from webtest import TestApp
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


class BasicCrudTest(unittest2.TestCase):
    def setUp(self):
        test_models.CreateAll()
        

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
        post_json_body = {'id': test_models.KEYS[name.upper()].integer_id()}
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
                                 {'id': test_models.KEYS[name.upper()].integer_id()},
                                 headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
        self.assertEquals('200 OK', response.status)
        self.assertIn('id', response)

    def tstUpdateOK(self):
        post_json_body = {'id': test_models.KEYS[name.upper()].integer_id()}
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
    
    
class ChoicesTest(unittest2.TestCase):
    def setUp(self):
        test_models.CreateAll()

    def testSupplier(self):
        post_json_body = {}
        response = app.post_json('/wsgi_service.supplier_choices_read',
                                 post_json_body,
                                 status=200,
                                 headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
        self.assertEquals('200 OK', response.status)
        self.assertDictEqual({u'choice': [{u'id': 7, u'label': u'House of Supply'}]}, response.json)
        
