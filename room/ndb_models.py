from google.appengine.ext import ndb

class StaffPosition(ndb.Model):
    """Staff positions that have hourly billing."""
    position_name = ndb.StringProperty()
    hourly_rate = ndb.FloatProperty(default=0.0)
    last_editor = ndb.UserProperty()
    modified = ndb.DateTimeProperty(auto_now=True)


class Staff(ndb.Model):
    name = ndb.StringProperty()
    email = ndb.StringProperty()
    email.unique = True
    email.required = True
