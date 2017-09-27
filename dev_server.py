import argparse
import sys
import time
import subprocess
import dev_utilities

parser = argparse.ArgumentParser()
parser.add_argument('dev_appserver_path', default='/google/google-cloud-sdk/bin/dev_appserver.py')

command = ['dev_appserver.py',
           '--clear_datastore=yes',
           '--admin_port', '8081',
           '--api_port', '8082',
           'app.yaml', '&']
try:
    subprocess.call(' '.join(command), shell=True)
except OSError:
    raise SystemExit("may not have been able to find dev_appserver.py, make sure your PATH is configured")

time.sleep(6)

dev_utilities.main(8080)

print("check out the local server at http://localhost:8080")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    subprocess.call('''ps -ef | grep app.yaml | grep api_port | awk '{print $2}' | xargs kill''', shell=True)
    sys.exit(0)