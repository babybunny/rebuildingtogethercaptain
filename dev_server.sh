#!/bin/bash 
# This starts the dev appserver, clears the datastore, and inserts some test data.

dev_appserver.py --clear_datastore=yes --port 8080 --admin_port 8081 --api_port 8082 app.yaml &

sleep 6

python dev_utilities.py


echo "check out the local server at http://localhost:8080"

wait
