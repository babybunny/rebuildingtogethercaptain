import os
import unittest

import path_utils

path_utils.fix_sys_path()

THIS_FILES_PATH = os.path.realpath(__file__)
SOURCE_ROOT = os.path.dirname(THIS_FILES_PATH)
TEST_DIRECTORY = os.path.join(SOURCE_ROOT, 'test')

assert os.path.isdir(TEST_DIRECTORY) and os.path.exists(os.path.join(TEST_DIRECTORY, 'test_main.py'))

loader = unittest.TestLoader()
suite = loader.discover(TEST_DIRECTORY)
runner = unittest.TextTestRunner(verbosity=2)
success = runner.run(suite).wasSuccessful()
if not success:
  raise SystemExit("Tests failed")
