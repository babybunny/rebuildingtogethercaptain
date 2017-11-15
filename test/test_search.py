import unittest

from test import app_engine_test_utils
from test import test_models


class TestSearch(unittest.TestCase):

  def setUp(self):
    app_engine_test_utils.activate_app_engine_testbed_and_clear_cache()
    self.model_keys = test_models.CreateAll()

  def test_search_orders(self):
    pass

if __name__ == '__main__':
  unittest.main()
