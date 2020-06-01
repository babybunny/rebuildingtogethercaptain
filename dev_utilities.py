import argparse
import logging
import urllib2
import time

import path_utils

path_utils.fix_sys_path()

from google.appengine.ext import ndb
from google.appengine.ext.remote_api import remote_api_stub

from test import test_models


def parse_port_from_command_line_args(default_port=8082):
  parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('--port', type=int,
                      help='localhost port number, matches API server port in dev_server.sh', default=default_port)

  args = parser.parse_args()
  return args.port


def init_stubs_and_models(port=None):
  port = port or parse_port_from_command_line_args()
  servername = 'localhost:{}'.format(port)
  remote_api_stub.RemoteStub._SetRequestId("otherwise it spams error messages")
  retries = 0
  while(retries < 4):
    try:
      remote_api_stub.ConfigureRemoteApi(
        app_id=None,  # don't contact prod server!
        servername=servername,
        path='/_ah/remote_api',
        auth_func=lambda: ('', ''),
        secure=False)
      logging.info('remote_api_stub.ConfigureRemoteApi success')
      break
    except urllib2.URLError, e:
      logging.warn('could not open URL for remote_api_stub.ConfigureRemoteApi, retrying.  %s' % e)
      retries += 1
      time.sleep(retries)

  logging.info("creating test models in the datastore ... this may take a few seconds")
  keys = test_models.CreateAll()
  logging.info("created %d test models", len(keys))

if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO, format='%(levelname)-8s %(asctime)s %(filename)s] %(message)s')
  init_stubs_and_models()
