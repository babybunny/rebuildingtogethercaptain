"""Main application, welcome screen."""
import logging
import os

import jinja2
import webapp2

from room import ndb_models

from google.appengine.api import oauth


class MainPage(webapp2.RequestHandler):
    """The main UI page, renders the 'index.html' template."""

    def get(self):
        """Renders the main page."""
        status = ''
        try: 
          user = oauth.get_current_user()
          status = 'signed in as %s' % user.email()
        except oauth.Error:
          status = 'not signed in'
        template_values = {
          'status': status,
        }
        template = jinja_environment.get_template('templates/index.html')
        self.response.out.write(template.render(template_values))


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
