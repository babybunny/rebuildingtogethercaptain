"""Main application, welcome screen."""
import logging
import os

import jinja2
import webapp2

from room import common
from room import ndb_models
from room import staff

from google.appengine.api import oauth

class MainPage(webapp2.RequestHandler):
    """The main UI page, renders the 'index.html' template."""

    def get(self):
        """Renders the main page."""
        user, status = common.GetUser()
        oauth_user = 'placeholder'
        template_values = dict(locals())
        template = jinja_environment.get_template('templates/index.html')
        self.response.out.write(template.render(template_values))


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/room/staff_home', staff.StaffHome),
], debug=True)
