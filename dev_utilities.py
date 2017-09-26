import argparse

try:
  import dev_appserver
except ImportError:
  print('Please make sure the App Engine SDK is in your PYTHONPATH.')
  raise

from google.appengine.ext import ndb
from google.appengine.ext.remote_api import remote_api_stub

from test import test_models


def main(port):
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
  parser = argparse.ArgumentParser(
      description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument(
      '--port', help='localhost port number, matches API server port in dev_server.sh', default=8082)

  args = parser.parse_args()

  main(args.port)
