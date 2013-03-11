"""Models that don't depend on Djangpo."""

from google.appengine.ext import db


class Program(db.Model):
    """Identifies a program like "National Rebuilding Day".

    Programs with status 'Active' will be visible to Captains.

    Keys are shorthand like "2012 NRD".
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

