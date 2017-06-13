#!/bin/bash -x -e

# clean up
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

# This starts the dev appserver, clears the datastore, and inserts some test data.

dev_appserver.py --clear_datastore=yes --port 9084 --admin_port 9085 --api_port 9086 app.yaml &

sleep 6

python dev_utilities.py


echo "check out the local server at http://localhost:9084"

wait
