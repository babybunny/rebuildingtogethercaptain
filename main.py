"""Main application, welcome screen."""
import logging
import os

import jinja2
import webapp2

from google.appengine.api import users

class MainPage(webapp2.RequestHandler):
    """The main UI page, renders the 'index.html' template."""

    def get(self):
        """Renders the welcome page or redirects to correct page if user is logged in and known."""
        user = users.get_current_user()
        template_values = {'user': user}
        template = jinja_environment.get_template('templates/welcome.html')
        self.response.out.write(template.render(template_values))

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

app = webapp2.WSGIApplication([
    ('/', MainPage)
], debug=True)
