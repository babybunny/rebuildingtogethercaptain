"""Main application, welcome screen."""
import logging
import os

import jinja2
import webapp2

from google.appengine.api import users

class MainPage(webapp2.RequestHandler):
    """The main UI page, renders the 'index.html' template."""

    def get(self):
        """Renders the main page."""
        template_values = {'show_admin_link': users.IsCurrentUserAdmin()}
        template = jinja_environment.get_template('templates/index.html')
        self.response.out.write(template.render(template_values))

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

app = webapp2.WSGIApplication([
    ('/.*', MainPage)
], debug=True)
