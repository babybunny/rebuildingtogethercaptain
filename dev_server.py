import subprocess
import sys
import time
import os
import dev_utilities

my_path = os.path.realpath(__file__)
app_yaml = os.path.join(os.path.dirname(my_path), 'gae', 'app.yaml')

command = ['dev_appserver.py',
           '--clear_datastore=yes',
           '--admin_port', '8081',
           '--api_port', '8082',
           app_yaml, '&']
try:
  return_code = subprocess.call(' '.join(command), shell=True)
except OSError:
  raise SystemExit("may not have been able to find dev_appserver.py, make sure your PATH is configured")

time.sleep(6)

dev_utilities.init_stubs_and_models(8080)

print("check out the local server at http://localhost:8080")

try:
  while True:
    time.sleep(1)
except KeyboardInterrupt:
  print("Received KeyboardInterrupt")
  sys.exit(0)
