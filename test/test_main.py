"""Functional tests for main views."""

import os
import unittest
from webtest import TestApp
import main
from test import test_models
import app_engine_test_utils

app = TestApp(main.app)


class WelcomeTest(unittest.TestCase):

    def setUp(self):
        app_engine_test_utils.activate_app_engine_testbed()
        app_engine_test_utils.clear_ndb_cache()

    def testHelp(self):
        response = app.get('/help')
        self.assertEquals('200 OK', response.status)

    def testRoot(self):
        os.environ['ROOMS_DEV_SIGNIN_EMAIL'] = "rebuildingtogether.nobody@gmail.com"
        response = app.get('/')
        self.assertEquals('200 OK', response.status)
        self.assertIn('Welcome to ROOMS', str(response))
        self.assertIn('rebuildingtogether.nobody@gmail.com', str(response))

    def testRootXHeader(self):
        response = app.get('/', headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
        self.assertEquals('200 OK', response.status)
        self.assertIn('rebuildingtogether.staff@gmail.com', str(response))


class StatefulTest(unittest.TestCase):
    def setUp(self):
        app_engine_test_utils.activate_app_engine_testbed()
        app_engine_test_utils.clear_ndb_cache()
        self.keys = test_models.CreateAll()
        test_models.CreateAll()        
                
    def testRootXHeaderStaff(self):
        response = app.get('/', headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
        self.assertEquals('302 Moved Temporarily', response.status)
        self.assertIn('Location', response.headers)
        self.assertIn('/staff_home', response.headers['Location'])
        self.assertIn('rebuildingtogether.staff@gmail.com', str(response))
        
    def testRootXHeaderCaptain(self):
        response = app.get('/', headers={'x-rooms-dev-signin-email': 'rebuildingtogether.capn@gmail.com'})
        self.assertEquals('302 Moved Temporarily', response.status)
        self.assertIn('Location', response.headers)
        self.assertIn('/captain_home', response.headers['Location'])
        self.assertIn('rebuildingtogether.capn@gmail.com', str(response))
