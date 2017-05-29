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
    program_selected = ndb.StringProperty()
    last_welcome = ndb.DateTimeProperty()
    notes = ndb.TextProperty()
    since = ndb.DateProperty(auto_now_add=True)

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

  def put(self, *a, **k):
    self.email = self.email.lower()
    prefixes = set()
    if self.name:
      prefixes.add(self.name)
      for part in self.name.split():
        prefixes.add(part)
        for i in xrange(1, 7):
          prefixes.add(part[:i])
    if self.email:
      prefixes.add(self.email)
      for i in xrange(1, 7):
        prefixes.add(self.email[:i])
    self.search_prefixes = [p.lower() for p in prefixes]
    super(BaseModel, self).put(*a, **k)

  def __unicode__(self):
    return self.name
  
  def Label(self):
    return "%s <%s>" % (self.name, self.email)
                                                                                                                
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


class Supplier(ndb.Model):
  """A supplier of Items."""
  name = ndb.StringProperty(required=True)
  email = ndb.StringProperty()
  address = ndb.StringProperty()
  phone1 = ndb.StringProperty()
  phone2 = ndb.StringProperty()
  notes = ndb.TextProperty()
  since = ndb.DateProperty(auto_now_add=True)
  active = ndb.StringProperty(choices=('Active', 'Inactive'),
                              default='Active')
  visibility = ndb.StringProperty(choices=('Everyone', 'Staff Only'),
                                  default='Everyone')
  
  def __unicode__(self):
    return self.name
  
  def __str__(self):
    return self.name


class OrderSheet(ndb.Model):
  """Set of items commonly ordered together.
  Corresponds to one of the old paper forms, like the Cleaning Supplies form.
  """
  name = ndb.StringProperty()
  visibility = ndb.StringProperty(choices=('Everyone', 'Staff Only'),
                                  default='Everyone')
  supports_extra_name_on_order = ndb.BooleanProperty(default=False)
  code = ndb.StringProperty()
  code.verbose_name = 'Three-letter code like LUM for Lumber'
  instructions = ndb.TextProperty(default='')
  instructions.verbose_name = (
    'Instructions to Captain, appears on order form')
  logistics_instructions = ndb.TextProperty(default='')
  logistics_instructions.verbose_name = (
    'Instructions to Captain, appears on logistics form')
  default_supplier = ndb.KeyProperty(kind=Supplier)
  default_supplier.verbose_name = (
    'Default Supplier, used if Item\'s supplier is not set.')
  # Choose one of the next three.
  delivery_options = ndb.StringProperty(choices=['Yes', 'No'], default='No')
  delivery_options.verbose_name = ('Allow Captain to select Delivery to site')
  pickup_options = ndb.StringProperty(choices=['Yes', 'No'], default='No')
  pickup_options.verbose_name = (
    'Allow Captain to select Pick-up from RTP warehouse')
  retrieval_options = ndb.StringProperty(choices=['Yes', 'No'], default='No')
  retrieval_options.verbose_name = ('Drop-off and retrieval (like debris box)'
                                    '  Note: do not set this with either'
                                    ' delivery or pick-up')
  
  def __unicode__(self):
    return '%s' % (self.name)
  
  def HasLogistics(self):
    return (self.delivery_options == 'Yes' or
            self.pickup_options == 'Yes' or
            self.retrieval_options == 'Yes')      



class Site(ndb.Model):
  """A work site."""
  # "10001DAL" reads: 2010, #001, Daly City
  number = ndb.StringProperty(required=True)  # unique
  program = ndb.StringProperty()  # reference
  name = ndb.StringProperty()  # "Belle Haven"
  name.verbose_name = 'Recipient Name'
  applicant = ndb.StringProperty()
  applicant.verbose_name = 'Applicant Contact'
  applicant_home_phone = ndb.StringProperty()
  applicant_work_phone = ndb.StringProperty()
  applicant_mobile_phone = ndb.StringProperty()
  applicant_email = ndb.StringProperty()
  rating = ndb.StringProperty()
  roof = ndb.StringProperty()
  rrp_test = ndb.StringProperty()
  rrp_level = ndb.StringProperty()
  jurisdiction = ndb.StringProperty()
  jurisdiction_choice = ndb.KeyProperty(kind=Jurisdiction)
  scope_of_work = ndb.TextProperty()
  sponsor = ndb.StringProperty()
  street_number = ndb.StringProperty()
  street_number.verbose_name = "Street Address"
  street_number.help_text = "Full street address like 960 Main Street, Apt 4"
  city_state_zip = ndb.StringProperty()
  city_state_zip.help_text = "City State Zip, like Menlo Park CA 94025"
  budget = ndb.IntegerProperty(default=0)
  announcement_subject = ndb.StringProperty(default='Nothing Needs Attention')
  announcement_body = ndb.TextProperty(
    default="Pat yourself on the back - no items need attention.\n"
    "You have a clean bill of health.")
  search_prefixes = ndb.StringProperty(repeated=True)
  photo_link = ndb.StringProperty()
  photo_link.help_text = "example: https://www.flickr.com/gp/rebuildingtogetherpeninsula/UX22iM/"
  volunteer_signup_link = ndb.StringProperty()
  volunteer_signup_link.help_text = "http://rebuildingtogetherpeninsula.force.com/GW_Volunteers__VolunteersJobListingFS?&CampaignID=701U0000000rnvU"


















    
