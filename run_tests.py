import argparse
import os
import sys
import unittest

THIS_FILES_PATH = os.path.realpath(__file__)
SOURCE_ROOT = os.path.dirname(THIS_FILES_PATH)
TEST_DIRECTORY = os.path.join(SOURCE_ROOT, 'test')

assert os.path.isdir(TEST_DIRECTORY) and os.path.exists(os.path.join(TEST_DIRECTORY, 'test_main.py'))

parser = argparse.ArgumentParser()
parser.add_argument('google_sdk_path', nargs='?',
                    help='Path to sdk home, eg /google/google-cloud-sdk/platform/google_appengine')
sdk_path = parser.parse_args().google_sdk_path
if sdk_path is None:
    parser.error("google_sdk_path is required")
if not os.path.isdir(sdk_path):
    parser.error("google_sdk_path={0} is not a directory".format(sdk_path))
if 'dev_appserver.py' not in os.listdir(sdk_path):
    parser.error("google_sdk_path={0} appears to be invalid, should contain dev_appserver.py".format(sdk_path))


# https://cloud.google.com/appengine/docs/standard/python/tools/localunittesting
sys.path.insert(1, sdk_path)
sys.path.insert(1, os.path.join(sdk_path, 'lib', 'yaml', 'lib'))
sys.path.insert(1, SOURCE_ROOT)

loader = unittest.TestLoader()
suite = loader.discover(TEST_DIRECTORY)
runner = unittest.TextTestRunner(verbosity=2)
runner.run(suite)
