"""Functional tests for main views."""

import os
import unittest2
from webtest import TestApp
import main
from test import test_models

app = TestApp(main.app)

class WelcomeTest(unittest2.TestCase):
    def testHelp(self):
        response = app.get('/help')
        self.assertEquals('200 OK', response.status)

    def testRoot(self):
        # determines dev user from nose2.cfg
        # testbed-env = ROOMS_DEV_SIGNIN_EMAIL="rebuildingtogether.nobody@gmail.com"
        response = app.get('/')
        self.assertEquals('200 OK', response.status)
        self.assertIn('Welcome to ROOMS', str(response))
        self.assertIn('rebuildingtogether.nobody@gmail.com', str(response))

    def testRootXHeader(self):
        response = app.get('/', headers={'X-ROOMS_DEV_SIGNIN_EMAIL': 'rebuildingtogether.staff@gmail.com'})
        self.assertEquals('200 OK', response.status)
        self.assertIn('rebuildingtogether.staff@gmail.com', str(response))


class StatefulTest(unittest2.TestCase):
    def setUp(self):
        test_models.CreateAll()        
                
    def testRootXHeaderStaff(self):
        response = app.get('/', headers={'X-ROOMS_DEV_SIGNIN_EMAIL': 'rebuildingtogether.staff@gmail.com'})
        self.assertEquals('302 Moved Temporarily', response.status)
        self.assertIn('Location', response.headers)
        self.assertIn('/staff_home', response.headers['Location'])
        self.assertIn('rebuildingtogether.staff@gmail.com', str(response))
        
    def testRootXHeaderCaptain(self):
        response = app.get('/', headers={'X-ROOMS_DEV_SIGNIN_EMAIL': 'rebuildingtogether.capn@gmail.com'})
        self.assertEquals('302 Moved Temporarily', response.status)
        self.assertIn('Location', response.headers)
        self.assertIn('/captain_home', response.headers['Location'])
        self.assertIn('rebuildingtogether.capn@gmail.com', str(response))
