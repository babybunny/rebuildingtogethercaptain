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

    def plain(self):
        return {
            'key': self.key().name(),
            'name': self.name,
            'year': self.year,
            'site_number_prefix': self.site_number_prefix,
            'status': self.status,
            }

class Staff(db.Model):
    """A RTP staff member."""
    name = db.StringProperty()
    email = db.EmailProperty()
    email.unique = True
    email.required = True
    # The key name of a Program, like "2013 NRD".
    program_selected = db.StringProperty()
    user = db.UserProperty()
    last_welcome = db.DateTimeProperty()
    notes = db.TextProperty()
    since = db.DateProperty(auto_now_add=True)


class PlainModelHandler(webapp.RequestHandler):
    """Requires self.model_class to point to a plain_model."""
    model_class = None

    def get(self):
        key = self.request.get('key')
        if key:
            p = self.model_class.get_by_key_name(key)
            if not p:
                self.abort(404)
            res = p.plain()
        else:
            res = []
            for p in self.model_class.all():
                res.append(p.plain())
            
        self.response.out.write(json.dumps(res))
        self.response.headers['Content-Type'] = 'application/json'


class StaffHandler(PlainModelHandler):
    model_class = Staff

    def post(self):
        """Only sets program_selected now."""
        attrs = json.loads(self.request.body)
        s = plain_models.Staff.get(key=db.Key(encoded=attrs['key']))
        s.program_selected = attrs['program_selected']
        s.put()
    

class ProgramHandler(PlainModelHandler):
    model_class = Program

    def post(self):
        """Simply over-write existing Program with same key."""
        attrs = json.loads(self.request.body)
        key = '%d %s' % (attrs['year'], attrs['name'])
        p = Program(key_name=key)
        p.name = attrs['name']
        p.year = attrs['year']
        p.site_number_prefix = attrs['site_number_prefix']
        p.put()


application = webapp.WSGIApplication(
    [
        ('/room/plain_models/Program', ProgramHandler),
        ('/room/plain_models/Staff', StaffHandler),
        ],
    debug=True
    )

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
