# ROOMs app for Rebuilding Together Peninsula

*Copyright 2010 Luke Stone*

This is an online ordering system for construction captains for the
annual Rebuilding Day.

### Developer Setup
1. [Install the google sdk](https://cloud.google.com/sdk/docs/)
1. `git clone git@github.com:babybunny/rebuildingtogethercaptain.git`
1. `cd rebuildingtogethercaptain`
1. `virtualenv virtualenv  # this directory name is .gitignored`
1. `./virtualenv/bin/pip install -r requirements.txt`
1. `./virtualenv/bin/python run_tests.py /path/to/google-sdk-install`  # run the tests
1. `./virtualenv/bin/python dev_server.py`  # start a dev server