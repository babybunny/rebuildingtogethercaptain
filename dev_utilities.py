import argparse

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
  print servername
  remote_api_stub.ConfigureRemoteApi(
    app_id=None,  # don't contact prod server!
    servername=servername,
    path='/_ah/remote_api',
    auth_func=lambda: ('', ''),
    secure=False)

  # List the first 10 keys in the datastore.
  keys = ndb.Query().fetch(10, keys_only=True)

  for key in keys:
    print(key)

  test_models.CreateAll()


if __name__ == '__main__':
  init_stubs_and_models()
