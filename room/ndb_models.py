"""ndb model definitions

Many of these are similar to models in models.py, which are Django models.  We
need these ndb versions for use with runtime: python27, which is required by 
endpoints.
"""
from google.appengine.ext import ndb


class Jurisdiction(ndb.Model):
  """A jurisdiction name for reporting purposes."""
  name = ndb.StringProperty()

  def __unicode__(self):
    return self.name

  def __str__(self):
    return self.name


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
    email = ndb.StringProperty(required=True)


class Captain(ndb.Model):
    """A work captain."""
    name = ndb.StringProperty(required=True)  # "Joe User"
    # Using the UserProperty seems to be more hassle than it's worth.
    # I was getting errors about users that didn't exist when loading sample
    # data.
    email = ndb.StringProperty()  # "joe@user.com"
    rooms_id = ndb.StringProperty()  # "R00011"
    phone_mobile = ndb.StringProperty()
    phone_work = ndb.StringProperty()
    phone_home = ndb.StringProperty()
    phone_fax = ndb.StringProperty()
    phone_other = ndb.StringProperty()
    tshirt_size = ndb.StringProperty(choices=(
      'Small',
      'Medium',
      'Large',
      'X-Large',
      '2XL',
      '3XL'))
    notes = ndb.TextProperty()
    last_welcome = ndb.DateTimeProperty()
    modified = ndb.DateTimeProperty(auto_now=True)
    last_editor = ndb.UserProperty(auto_current_user=True)
    search_prefixes = ndb.StringProperty(repeated=True)


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


