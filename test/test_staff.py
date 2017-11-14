"""Functional tests for staff views."""

import unittest

from webtest import TestApp
import os
import app_engine_test_utils
from gae import main
from gae.room import staff, common
from test import route_lister
from test import test_models

APP = TestApp(main.app)


class LoggedInTest(unittest.TestCase):
  def setUp(self):
    os.environ[common.RoomsUser.DEV_EMAIL_ENVVAR] = 'rebuildingtogether.staff@gmail.com'
    app_engine_test_utils.activate_app_engine_testbed_and_clear_cache()

  def testStaffHome(self):
    response = APP.get('/room/staff_home')
    self.assertEquals('302 Moved Temporarily', response.status)
    # TODO: this could be more robust.  no guarantee that it's localhost?
    self.assertEquals('http://localhost/', response.headers['Location'])


class StatefulTestNoProgram(unittest.TestCase):
  def setUp(self):
    app_engine_test_utils.activate_app_engine_testbed_and_clear_cache()

    self.keys = test_models.CreateAll()

  def tearDown(self):
    test_models.DeleteAll(self.keys)

  def testHomeXHeaderStaff(self):
    response = APP.get('/room/staff_home', headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff2@gmail.com'})
    self.assertEquals('302 Moved Temporarily', response.status)
    self.assertEquals('http://localhost/room/select_program', response.headers['Location'])


class StatefulTestCaptain(unittest.TestCase):
  def setUp(self):
    app_engine_test_utils.activate_app_engine_testbed_and_clear_cache()

    self.keys = test_models.CreateAll()
    s = self.keys['STAFF'].get()
    s.program_selected = '2011 Test'
    s.put()

  def tearDown(self):
    test_models.DeleteAll(self.keys)

  def _get(self, path):
    return APP.get(path, headers={'x-rooms-dev-signin-email': 'rebuildingtogether.capn@gmail.com'})

  def testCaptainHome(self):
    response = self._get('/room/captain_home')
    self.assertIn('Ahoy Captain!', response.body)


class StatefulTestStaffWithProgram(unittest.TestCase):
  def setUp(self):
    app_engine_test_utils.activate_app_engine_testbed_and_clear_cache()

    self.keys = test_models.CreateAll()
    s = self.keys['STAFF'].get()
    s.program_selected = '2011 Test'
    s.put()

  def tearDown(self):
    test_models.DeleteAll(self.keys)

  def _get(self, path):
    return APP.get(path, headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'})

  def _post(self, path):
    return APP.post(path,
                    headers={'x-rooms-dev-signin-email': 'rebuildingtogether.staff@gmail.com'},
                    params={'submit': staff.EXPORT_CSV})


class StatefulTestStaffWithProgramAuto(StatefulTestStaffWithProgram):
  """Automatically test all routes to ensure they don't crash."""
  _multiprocess_can_split_ = True

  @staticmethod
  def get_test_function(path, method):

    def get(_self):
      response = _self._get(path)
      _self.assertEquals('200 OK', response.status, msg=str(response))

    def post(_self):
      response = _self._post(path)
      _self.assertEquals('200 OK', response.status, msg=str(response))

    if method == 'GET':
      return get
    if method == 'POST':
      return post
    raise NotImplementedError('method={0} not supported'.format(method))

  @staticmethod
  def build():
    for r in route_lister.get_route_list(main.login_required):
      if '<' in r['template']:
        continue  # TODO: figure out how to test paths with id segments.
      testFunc = StatefulTestStaffWithProgramAuto.get_test_function(r['template'], 'GET')
      testFunc.__name__ = 'test{}'.format(r['name'])
      setattr(StatefulTestStaffWithProgramAuto, testFunc.__name__, testFunc)

    for r in route_lister.get_route_list(main.post_routes):
      if '<' in r['template']:
        continue  # TODO: figure out how to test paths with id segments.
      testFunc = StatefulTestStaffWithProgramAuto.get_test_function(r['template'], 'POST')
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
    response = self._get('/room/site/view/{:d}/'.format(self.keys['SITE'].integer_id()))
    self.assertEquals('200 OK', response.status)
    self.assertIn('2011 Test', response.body)
    self.assertIn('110TEST', response.body)
    self.assertIn('Miss Captain', response.body)

  def testOrderView(self):
    response = self._get('/room/order_view/{:d}'.format(self.keys['ORDER'].integer_id()))
    self.assertEquals('200 OK', response.status)
    self.assertIn('110TEST', response.body)
    self.assertIn('My First Item', response.body)
    self.assertIn('Acorn City', response.body)

    def testOrderReconcile(self):
        response = self._get('/room/order_reconcile/{:d}'.format(self.keys['ORDERSHEET'].integer_id()))
        self.assertEquals('200 OK', response.status)
        self.assertIn('Being Filled', response.body)

        
StatefulTestStaffWithProgramAuto.build()

if __name__ == '__main__':
  unittest.main()
