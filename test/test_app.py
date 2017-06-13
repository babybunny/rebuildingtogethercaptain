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
        # testbed-env = ROOMS_DEV_SIGNIN_EMAIL="rebuildingtogether.staff@gmail.com"
        response = app.get('/')
        
