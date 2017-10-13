import unittest

import path_utils
from gae.room.migrations.october_2017_migration import October2017Migration

path_utils.fix_sys_path()
from test import app_engine_test_utils
from test import test_models_v1


class TestOctober2017Migration(unittest.TestCase):

  def setUp(self):
    app_engine_test_utils.activate_app_engine_testbed_and_clear_cache()
    self._keys = test_models_v1.CreateAll()

  def test_migrations(self):
    migrator = October2017Migration()
    migrator.update()
