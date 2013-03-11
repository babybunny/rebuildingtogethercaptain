"""App and handlers for JSON data export.

Intended to be consumed by AngularJS app.
Complements the automatic REST services in rest/.
Does not use Django.
"""

import json
import webapp2
from google.appengine.api import users
from room import plain_models


class User(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        user = users.GetCurrentUser()
        staff = plain_models.Staff.all().filter('email = ', user.email().lower()).get()
        user_d = dict(email=user.email())
        if staff:
            user_d['program_selected'] = staff.program_selected
        else:
            user_d['program_selected'] = None
        
        self.response.write(json.dumps(user_d))


app = webapp2.WSGIApplication([('/room/data/User', User)],
                              debug=True)
