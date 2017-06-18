"""Functional tests for staff views."""

import os
import unittest2
import webapp2
from webtest import TestApp
import main
from test import test_models
from test import route_lister

app = TestApp(main.app)


class LoggedInTest(unittest2.TestCase):
    def testStaffHome(self):
        response = app.get('/room/staff_home')
        self.assertEquals('302 Moved Temporarily', response.status)
        # TODO: this could be more robust.  no guarantee that it's localhost?
        self.assertEquals('http://localhost/', response.headers['Location'])

        
class StatefulTestNoProgram(unittest2.TestCase):
    def setUp(self):
        test_models.CreateAll()        
                
    def testHomeXHeaderStaff(self):
        response = app.get('/room/staff_home', headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
        self.assertEquals('302 Moved Temporarily', response.status)
        self.assertEquals('http://localhost/room/select_program', response.headers['Location'])
        

class StatefulTestCaptain(unittest2.TestCase):
    def setUp(self):
        test_models.CreateAll()        
        s = test_models.KEYS['STAFF'].get()
        s.program_selected = '2011 Test'
        s.put()

    def _get(self, path):
        return app.get(path, headers={'x-rooms-dev-signin-email': 'rebuildingtogether.capn@gmail.com'})

    def testCaptainHome(self):
        response = self._get('/room/captain_home')
        self.assertIn('Ahoy Captain!', response.body)
        
    
class StatefulTestStaffWithProgram(unittest2.TestCase):
    def setUp(self):
        test_models.CreateAll()        
        s = test_models.KEYS['STAFF'].get()
        s.program_selected = '2011 Test'
        s.put()

    def _get(self, path):
        return app.get(path, headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})
        
    
class StatefulTestStaffWithProgramAuto(StatefulTestStaffWithProgram):
    """Automatically test all routes to ensure they don't crash."""
    _multiprocess_can_split_ = True

def _makerOfTestFunction(path):
    """Return a test function for the path"""
    def aTest(self):
        response = self._get(path)
        self.assertEquals('200 OK', response.status, msg=str(response))
    return aTest

routes = route_lister.get_route_list(main.login_required)

for r in routes:
    if '<' in r['template']:
        continue  # TODO: figure out how to test paths with id segments.
    testFunc = _makerOfTestFunction(r['template'])
    testFunc.__name__ = 'test{}'.format(r['name'])
    setattr(StatefulTestStaffWithProgramAuto, testFunc.__name__, testFunc)
        

class StatefulTestStaffWithProgramCustom(StatefulTestStaffWithProgram):
    """Test specific routes with a certain degree of intelligence."""
    def testStaffHome(self):
        response = self._get('/room/staff_home')
        self.assertEquals('200 OK', response.status)
        self.assertIn('2011 Test', str(response))
        self.assertIn('Hello RTP Staff', str(response))

    def testSelectProgram(self):
        response = self._get('/room/select_program')
        self.assertEquals('200 OK', response.status)
        self.assertIn('Select a Program', str(response))
        self.assertIn('2011 Test', str(response))
        self.assertIn('/room/select_program?program=2011 Test', str(response))

    def testSitesAndCaptains(self):
        response = self._get('/room/sites_and_captains')
        self.assertEquals('200 OK', response.status)
        self.assertIn('2011 Test', str(response))
        self.assertIn('Miss Captain', str(response))
        
    def testSiteView(self):
        response = self._get('/room/site/view/{:d}/'.format(test_models.KEYS['SITE'].integer_id()))
        self.assertEquals('200 OK', response.status)
        self.assertIn('2011 Test', response.body)
        self.assertIn('110TEST', response.body)
        self.assertIn('Miss Captain', response.body)
