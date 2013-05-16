"""Models that don't depend on Djangpo."""
import logging
import json

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app


class Program(db.Model):
    """Identifies a program like "National Rebuilding Day".

    Programs with status 'Active' will be visible to Captains.

    Keys are shorthand like "2012 NRD", which is the year and name combined.
    """
    year = db.IntegerProperty()
    name = db.StringProperty()
    site_number_prefix = db.StringProperty()
    status = db.StringProperty(choices=('Active', 'Inactive'), 
                               default='Inactive')


class Staff(db.Model):
    """A RTP staff member."""
    name = db.StringProperty()
    email = db.EmailProperty()
    email.unique = True
    email.required = True
    program_selected = db.StringProperty()
    user = db.UserProperty()
    last_welcome = db.DateTimeProperty()
    notes = db.TextProperty()
    since = db.DateProperty(auto_now_add=True)


class ProgramHandler(webapp.RequestHandler):
    def get(self):
        res = []
        for p in Program.all():
            res.append({
                    'key': p.key().name(),
                    'name': p.name,
                    'year': p.year,
                    'site_number_prefix': p.site_number_prefix,
                    'status': p.status,
                    })
            
        self.response.out.write(json.dumps(res))
        self.response.headers['Content-Type'] = 'application/json'

    def post(self):
        attrs = json.loads(self.request.body)
        key = '%d %s' % (attrs['year'], attrs['name'])
        p = Program(key_name=key)
        p.name = attrs['name']
        p.year = attrs['year']
        p.site_number_prefix = attrs['site_number_prefix']
        p.put()


application = webapp.WSGIApplication(
    [
        ('/room/plain_models/Program', ProgramHandler)
        ],
    debug=True
    )

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
