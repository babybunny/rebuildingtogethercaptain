import collections

import logging
from google.appengine.ext import ndb

from room import ndb_models
from room.models.program import Program


class Site(ndb.Model):
  """
  new model for a work site as of October 2017
  """

  # "10001DAL" reads: 2010, #001, Daly City
  number = ndb.StringProperty(required=True)  # unique
  program_id = ndb.IntegerProperty(required=True)  # reference
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
  jurisdiction_choice = ndb.KeyProperty(kind=ndb_models.Jurisdiction)
  scope_of_work = ndb.TextProperty()
  sponsor = ndb.StringProperty()
  street_number = ndb.StringProperty()
  street_number.verbose_name = "Street Address"
  city_state_zip = ndb.StringProperty()
  budget = ndb.IntegerProperty(default=0)
  announcement_subject = ndb.StringProperty(default='Nothing Needs Attention')
  announcement_body = ndb.TextProperty(
    default="Pat yourself on the back - no items need attention.\n"
            "You have a clean bill of health.")
  search_prefixes = ndb.StringProperty(repeated=True)
  photo_link = ndb.StringProperty()
  volunteer_signup_link = ndb.StringProperty()
  latest_computed_expenses = ndb.FloatProperty()

  @property
  def IsCDBG(self):
    return 'CDBG' in self.jurisdiction

  @property
  def ContactPerson(self):
    if self.applicant:
      return self.applicant
    return self.name

  @property
  def Orders(self):
    return ndb_models._ActiveItems(self, ndb_models.Order)

  @property
  def CheckRequests(self):
    return ndb_models._ActiveItems(self, ndb_models.CheckRequest)

  @property
  def VendorReceipts(self):
    return ndb_models._ActiveItems(self, ndb_models.VendorReceipt)

  @property
  def InKindDonations(self):
    return ndb_models._ActiveItems(self, ndb_models.InKindDonation)

  @property
  def StaffTimes(self):
    return ndb_models._ActiveItems(self, ndb_models.StaffTime)

  @property
  def StaffTimesByPosition(self):
    class Pos(object):

      def __init__(self):
        self.name = None
        self.hours = 0.0
        self.hours_subtotal = 0.0
        self.miles = 0.0
        self.mileage_subtotal = 0.0
        self.stafftimes = []

    by_pos = collections.defaultdict(Pos)
    for s in self.StaffTimes:
      name = str(s.position.get())
      pos = by_pos[name]
      if pos.name is None:
        pos.name = name
      pos.stafftimes.append(s)
      pos.hours += s.hours
      pos.hours_subtotal += s.HoursTotal()
      pos.miles += s.miles
      pos.mileage_subtotal += s.MileageTotal()
    return list(by_pos.itervalues())

  @property
  def ScopeOfWork(self):
    if self.scope_of_work:
      return self.scope_of_work
    sow = ''
    for o in self.Orders:
      if o.order_sheet.get().name == 'Scope of Work':
        sow = o.notes
    self.scope_of_work = sow
    self.put()
    return sow

  def SaveTheChildren(self):
    for child in (self.Orders, self.CheckRequests,
                  self.VendorReceipts, self.InKindDonations,
                  self.StaffTimes):
      for obj in child:
        obj.put()

  def put(self, *a, **k):
    if self.jurisdiction_choice:
      self.jurisdiction = self.jurisdiction_choice.get().name
    # issue213: program should be configurable
    if not self.program:
      self.program = Program.from_site_number(self.number).key.integer_id()
    prefixes = set()
    for f in self.name, self.applicant, self.street_number, self.jurisdiction:
      if not f:
        continue
      prefixes.add(f)
      for part in f.split():
        prefixes.add(part)
        for i in xrange(1, 7):
          prefixes.add(part[:i])

    if self.number:
      prefixes.add(self.number)
      for i in xrange(1, 7):
        prefixes.add(self.number[:i])
        prefixes.add(self.number[2:2 + i])
        prefixes.add(self.number[5:5 + i])
    self.search_prefixes = [p.lower() for p in prefixes]
    logging.info('prefixes for %s: %s', self.number, self.search_prefixes)
    k = super(ndb_models.NewSite, self).put(*a, **k)
    return k

  def Label(self):
    return "%s %s" % (self.number, self.name)

  def __unicode__(self):
    """Only works if self has been saved."""
    return 'Site #%s | %s' % (self.number, self.name)

  def StreetAddress(self):
    if not self.street_number or not self.city_state_zip:
      return "TODO - enter an address"
    return '%s, %s' % (' '.join(self.street_number.split()),
                       ' '.join(self.city_state_zip.split()))

  def NeedsAttention(self):
    return self.announcement_subject is not None

  @property
  def sitecaptain_set(self):
    return ndb_models.SiteCaptain.query(ndb_models.SiteCaptain.site == self.key)

  def OrderTotal(self):
    """Only works if self has been saved."""
    cost = sum(order.GrandTotal() for order in self.Orders)
    return cost

  @property
  def order_total(self):
    if not hasattr(self, '_order_total'):
      self._order_total = self.OrderTotal()
    return self._order_total

  def CheckRequestTotal(self):
    """Only works if self has been saved."""
    return sum(cr.Total() or 0 for cr in self.CheckRequests)

  def VendorReceiptTotal(self):
    """Only works if self has been saved."""
    return sum(cr.amount or 0 for cr in self.VendorReceipts)

  def InKindDonationTotal(self):
    """Only works if self has been saved."""
    return sum(cr.Total() or 0 for cr in self.InKindDonations)

  def StaffTimeTotal(self):
    """Only works if self has been saved."""
    return sum(cr.Total() or 0 for cr in self.StaffTimes)

  def RecomputeExpenses(self):
    logging.info('Recomputing expenses for %s', self.number)
    self.latest_computed_expenses = (
      self.order_total +
      self.CheckRequestTotal() +
      self.StaffTimeTotal() +
      self.VendorReceiptTotal())
    self.put()

  def Expenses(self):
    if self.latest_computed_expenses is None:
      self.RecomputeExpenses()
    return self.latest_computed_expenses

  def BudgetRemaining(self):
    if self.budget:
      return self.budget - self.Expenses()
    else:
      return 0.

  @property
  def budget_remaining(self):
    if not hasattr(self, '_budget_remaining'):
      self._budget_remaining = self.BudgetRemaining()
      return self._budget_remaining

  @property
  def in_the_red(self):
    return self.budget_remaining < 0

  def BudgetStatement(self):
    if self.BudgetRemaining() > 0:
      return '$%0.2f unspent budget' % self.BudgetRemaining()
    elif self.BudgetRemaining() < 0:
      return '$%0.2f over budget' % (-1 * self.BudgetRemaining())
    else:
      return ''