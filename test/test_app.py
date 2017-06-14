"""Functional tests for Staff views."""

import os
import unittest2
from webtest import TestApp
import main


app = TestApp(main.app)

class StaffTest(unittest2.TestCase):
    def testHelp(self):
        response = app.get('/help')

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
