"""ndb model definitions

Many of these are similar to models in models.py, which are Django models.  We
need these ndb versions for use with runtime: python27, which is required by 
endpoints.
"""
from google.appengine.ext import ndb

# This needs an edit as it's diverged from the model in the master branch.
class StaffPosition(ndb.Model):
    """Staff positions that have hourly billing."""
    position_name = ndb.StringProperty()
    hourly_rate = ndb.FloatProperty(default=0.0)
    last_editor = ndb.UserProperty()
    modified = ndb.DateTimeProperty(auto_now=True)


class Staff(ndb.Model):
    """Minimal variant of the Staff model.

    For use in authorization within endpoints.
    """
    name = ndb.StringProperty()
    email = ndb.StringProperty()
    email.unique = True
    email.required = True


class Program(ndb.Model):
    """Identifies a program like "National Rebuilding Day".

    Programs with status 'Active' will be visible to Captains.

    Keys are shorthand like "2012 NRD".
    """
    year = ndb.IntegerProperty()
    name = ndb.StringProperty()
    site_number_prefix = ndb.StringProperty()
    status = ndb.StringProperty(choices=('Active', 'Inactive'), 
                                default='Inactive')
