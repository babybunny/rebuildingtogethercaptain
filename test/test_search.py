import unittest

from gae.room import ndb_models, staff
from gae.room.staff import MagicSearch
from test import app_engine_test_utils
from test import test_models

from google.appengine.api import search


class TestSearch(unittest.TestCase):

  def setUp(self):
    app_engine_test_utils.activate_app_engine_testbed_and_clear_cache()
    self.model_keys = test_models.CreateAll()

  def testSearchStaff(self):
    """
    ref: https://cloud.google.com/appengine/docs/standard/python/search/query_strings
    """
    index = search.Index('Staff')
    results = index.search('name: Mister Staff').results
    self.assertEqual(2, len(results))
    email_fields = [s.fields[-1] for s in results]
    self.assertTrue(all(isinstance(f, search.TextField) for f in email_fields))
    self.assertTrue(all(f.name == 'email' for f in email_fields))

  def testSearchNumericallyAndByDate(self):
    """
    ref: https://cloud.google.com/appengine/docs/standard/python/search/query_strings
    """
    index = search.Index('NewSite')
    self.assertEqual(2, len(index.search('budget < 1').results))
    self.assertEqual(1, len(index.search('budget = 5000').results))

    index = search.Index('Captain')
    self.assertEqual(0, len(index.search('last_welcome < 2017-01-01').results))
    self.assertEqual(1, len(index.search('last_welcome = 2017-01-30 ').results))

  def testMagicSearch(self):
    model, handler = MagicSearch.get_top_model_and_handler_for_search_string(u'110TEST')
    self.assertIsInstance(model, ndb_models.NewSite)
    self.assertEqual(model.number, '110TEST')
    self.assertEqual(handler, staff.SiteView)

if __name__ == '__main__':
  unittest.main()
