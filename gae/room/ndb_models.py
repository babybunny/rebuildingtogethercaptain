"""ndb model definitions

Many of these are similar to models in models.py, which are Django models.  We
need these ndb versions for use with runtime: python27, which is required by
endpoints.
"""
import collections
import logging
import math

from google.appengine.ext import ndb
from google.appengine.api import search

# TODO: move to global config
from gae.room import general_utils

SALES_TAX_RATE = 0.0925


def _SortItemsWithSections(items):
  """Sort a list of items so they look OK in the UI."""
  items.sort(
    key=lambda x: (x.order_form_section or None, x.name))
  prev_section = None
  for i in items:
    new_section = i.order_form_section or None
    if prev_section != new_section:
      i.first_in_section = True
    prev_section = new_section


class _ActiveItems(object):
  """Similar to backreference "*_set" properties in the old db interface."""

  def __init__(self, ref, kind_cls):
    """
    Args:
      ref: instance of a model that is referenced by another kind of model
      kind_cls: ndb kind to be selected, like in Key(kind=kind_cls)
    """
    self._query = kind_cls.query(kind_cls.site == ref.key,
                                 kind_cls.state != 'new',
                                 kind_cls.state != 'deleted',
                                 kind_cls.state != 'Deleted'
                                 )

  def Count(self):
    return self._query.count()

  def Items(self):
    for item in sorted(self._query,
                       key=lambda o: o.modified, reverse=True):
      yield item

  def __iter__(self):
    return self.Items()


class SearchableModel(ndb.Model):

  def get_search_result_headline(self):
    return "{} id={}".format(type(self), self.key.integer_id())

  def get_search_result_detail_lines(self):
    return ["{}: {}".format(prop, getattr(self, prop)) for prop in self._properties]

  @staticmethod
  def get_search_order():
    """override with lower number to search this index first"""
    return 1e10

  def get_canonical_request_response(self, request):
    """override to build a default response to requests whose search resolve to this model"""
    raise NotImplementedError("{} has no canonical request response defined".format(self.__class__.__name__))

  def get_indexed_fields(self):
    fields = []
    for prop_name, prop in self._properties.items():
      value = getattr(self, prop_name)
      if value is None:
        continue

      prop_type = type(prop)
      value_processor = lambda v: v
      if prop_type in (ndb.TextProperty, ndb.StringProperty):
        search_type = search.TextField

      elif prop_type in (ndb.FloatProperty, ndb.IntegerProperty):
        search_type = search.NumberField

      elif prop_type in (ndb.DateProperty, ndb.DateTimeProperty):
        search_type = search.DateField

      elif prop_type == ndb.UserProperty:
        search_type = search.TextField
        value_processor = lambda v: v.email()

      elif prop_type == ndb.KeyProperty:
        search_type = search.TextField
        value_processor = lambda v: unicode(v.id())

      elif prop_type == ndb.BooleanProperty:
        search_type = search.AtomField
        value_processor = lambda v: unicode(v)

      else:
        logging.warning("type {} not supported {}".format(prop_type, SearchableModel.__name__))
        continue


      if prop._repeated:
        for s in value:
          fields.append(search_type(name=prop_name, value=value_processor(s)))
      else:
        try:
          fields.append(search_type(name=prop_name, value=value_processor(value)))
        except TypeError:
          raise
    return fields

  def _post_put_hook(self, future):
    put_result = future.get_result()  # blocks on put but not a bad idea anyway
    model_key_id = put_result.integer_id()
    index_name = self.__class__.__name__
    index = search.Index(index_name)
    self.delete_by_model_key_id(model_key_id)
    fields = [
      search.AtomField(name="model_name", value=index_name),
      search.AtomField(name="model_key_id", value=unicode(model_key_id)),
      search.TextField(name='headline', value=self.get_search_result_headline())
    ]
    for detail in self.get_search_result_detail_lines():
      fields.append(search.TextField(name='details', value=detail))
    fields.extend(self.get_indexed_fields())
    doc = search.Document(doc_id=unicode(self.key.integer_id()), fields=fields)
    index.put(doc)

  @classmethod
  def delete_by_model_key_id(cls, model_key_id):
    index_name = cls.__name__
    index = search.Index(index_name)
    index.delete(document_ids=map(lambda d: d.doc_id, index.search("model_key_id={}".format(model_key_id))))

  @classmethod
  def _post_delete_hook(cls, key, future):
    cls.delete_by_model_key_id(key.id())


class Jurisdiction(SearchableModel):
  """A jurisdiction name for reporting purposes."""
  name = ndb.StringProperty()

  def __unicode__(self):
    return self.name

  def __str__(self):
    return self.name


class Staff(SearchableModel):
  """Minimal variant of the Staff model.

  For use in authorization within endpoints.
  """
  name = ndb.StringProperty()
  email = ndb.StringProperty(required=True)
  program_selected = ndb.StringProperty()
  last_welcome = ndb.DateProperty(auto_now=True)
  notes = ndb.TextProperty()
  since = ndb.DateProperty(auto_now_add=True)


class Captain(SearchableModel):
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
    return super(Captain, self).put(*a, **k)

  def __unicode__(self):
    return self.name

  def Label(self):
    return "%s <%s>" % (self.name, self.email)


class Program(SearchableModel):
  """Identifies a program like "National Rebuilding Day".

  Programs with status 'Active' will be visible to Captains.

  Keys are shorthand like "2012 NRD".
  """
  year = ndb.IntegerProperty()
  name = ndb.StringProperty()
  site_number_prefix = ndb.StringProperty()
  status = ndb.StringProperty(choices=('Active', 'Inactive'),
                              default='Inactive')


class Supplier(SearchableModel):
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


class OrderSheet(SearchableModel):
  """Set of items commonly ordered together.
  Corresponds to one of the old paper forms, like the Cleaning Supplies form.
  """
  name = ndb.StringProperty()
  visibility = ndb.StringProperty(choices=('Everyone', 'Staff Only'),
                                  default='Everyone')
  supports_extra_name_on_order = ndb.BooleanProperty(default=False)
  supports_internal_invoice = ndb.BooleanProperty(default=False)
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

  @property
  def item_set(self):
    return Item.query(Item.appears_on_order_form == self.key)


class Item(SearchableModel):
  """Represents a type of thing that may in the inventory."""
  bar_code_number = ndb.IntegerProperty()
  # bar_code_number.unique = True
  name = ndb.StringProperty(required=True)
  # name.unique = True
  appears_on_order_form = ndb.KeyProperty(kind=OrderSheet)
  order_form_section = ndb.StringProperty()
  description = ndb.StringProperty()
  # 'Each' 'Box' 'Pair' etc
  measure = ndb.StringProperty(
    choices=('Each', 'Roll', 'Bottle', 'Box', 'Pair', 'Board', 'Bundle',
             'Bag', 'Ton', 'Yard', 'Sheet', 'Cartridge', 'Tube', 'Tub',
             'Sq. Yds.', 'Gallon', 'Section', 'Home', 'Box', 'Drop-off',
             '', 'Other'))
  # Dollars.
  unit_cost = ndb.FloatProperty()
  must_be_returned = ndb.StringProperty(choices=['Yes', 'No'], default='No')
  picture = ndb.BlobProperty()
  thumbnail = ndb.BlobProperty()
  supplier = ndb.KeyProperty(kind=Supplier)
  supplier_part_number = ndb.StringProperty()
  url = ndb.StringProperty()
  last_editor = ndb.UserProperty()
  created = ndb.DateTimeProperty(auto_now_add=True)
  modified = ndb.DateTimeProperty(auto_now=True)
  supports_extra_name_on_order = ndb.BooleanProperty(default=False)

  def __unicode__(self):
    return self.description

  def VisibleSortableLabel(self, label):
    """Strips numeric prefixes used for sorting.

    Labels may have a digit prefix which is used for sorting, but
    should not be shown to users.
    """
    if not label:
      return ''
    parts = label.split()
    if len(parts) > 0 and parts[0].isdigit():
      return ' '.join(parts[1:])
    return label

  def VisibleName(self):
    return self.VisibleSortableLabel(self.name)

  def VisibleOrderFormSection(self):
    return self.VisibleSortableLabel(self.order_form_section)


class NewSite(SearchableModel):
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

  @staticmethod
  def get_search_order():
    return 0

  def get_search_result_headline(self):
    return "Site {}".format(self.number)

  def get_search_result_detail_lines(self):
    return [self.street_number or "N/A", self.city_state_zip]

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
    return _ActiveItems(self, Order)

  @property
  def CheckRequests(self):
    return _ActiveItems(self, CheckRequest)

  @property
  def VendorReceipts(self):
    return _ActiveItems(self, VendorReceipt)

  @property
  def InKindDonations(self):
    return _ActiveItems(self, InKindDonation)

  @property
  def StaffTimes(self):
    return _ActiveItems(self, StaffTime)

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

  def ProgramFromNumber(self):
    year = '20' + self.number[0:2]
    mode = self.number[2]
    program = None
    if mode == '0':
      program = year + ' NRD'
    elif mode == '1':
      program = year + ' NRD'
    elif mode == '3':
      program = year + ' Misc'
    elif mode == '5':
      program = year + ' Safe'
    elif mode == '6':
      program = year + ' Safe'
    elif mode == '7':
      program = year + ' Energy'
    elif mode == '8':
      program = year + ' Teambuild'
    elif mode == '9':
      program = year + ' Youth'
    elif mode == 'Z':
      program = year + ' Test'
    else:
      logging.warn('no program for site number %s', self.number)
    return program

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
      self.program = self.ProgramFromNumber()
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
    k = super(NewSite, self).put(*a, **k)
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
    return SiteCaptain.query(SiteCaptain.site == self.key)

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


class SiteCaptain(SearchableModel):
  """Associates a site and a Captain."""
  site = ndb.KeyProperty(kind=NewSite, required=True)
  captain = ndb.KeyProperty(kind=Captain, required=True)
  type = ndb.StringProperty(choices=(
    'Construction',
    'Team',
    'Volunteer',
  ))


class InvoiceNumber(SearchableModel):
  """Simple counter for invoice numbers.

  Currently there's a singleton with a Key(InvoiceNumber, 'global')
  """
  next_invoice_number = ndb.IntegerProperty()


class OrderInvoice(SearchableModel):
  """An internal invoice number that an Order can point at.

  Parent is the InvoiceNumber that generates the invoice_number value.
  """
  invoice_number = ndb.IntegerProperty()


class Order(SearchableModel):
  """A Captain can make an Order for a list of Items."""
  site = ndb.KeyProperty(kind=NewSite, required=True)
  order_sheet = ndb.KeyProperty(kind=OrderSheet, required=True)
  program = ndb.StringProperty()
  sub_total = ndb.FloatProperty()
  notes = ndb.TextProperty()
  state = ndb.StringProperty()
  actual_total = ndb.FloatProperty()
  reconciliation_notes = ndb.TextProperty(default='')
  invoice_date = ndb.DateProperty()
  internal_invoice = ndb.KeyProperty(kind=OrderInvoice)
  vendor = ndb.KeyProperty(kind=Supplier)
  logistics_start = ndb.StringProperty()
  logistics_end = ndb.StringProperty()
  logistics_instructions = ndb.TextProperty()
  created = ndb.DateTimeProperty(auto_now_add=True)
  created_by = ndb.UserProperty(auto_current_user_add=True)
  modified = ndb.DateTimeProperty(auto_now=True)
  last_editor = ndb.UserProperty(auto_current_user=True)

  @staticmethod
  def get_search_order():
    return 1

  @property
  def name(self):
    return '%s %s' % (self.site.get().number, self.order_sheet.get().name)

  @property
  def OrderItems(self):
    return OrderItem.query(OrderItem.order == self.key)

  @property
  def orderdelivery_set(self):
    return OrderDelivery.query(OrderDelivery.order == self.key)

  @property
  def orderpickup_set(self):
    return OrderPickup.query(OrderPickup.order == self.key)

  @property
  def orderretrieval_set(self):
    return OrderRetrieval.query(OrderRetrieval.order == self.key)

  def put(self, *a, **k):
    self.program = self.site.get().program
    me = super(Order, self).put(*a, **k)
    self.site.get().RecomputeExpenses()
    return me

  def SetInvoiceNumber(self):
    """Sets order_invoice field to an OrderInvoice with a unique invoice_number."""
    if self.internal_invoice:
      return

    @ndb.transactional()
    def _NewInvoiceNumber():
      ink = ndb.Key(InvoiceNumber, 'global')
      ino = ink.get()
      oio = OrderInvoice(invoice_number=ino.next_invoice_number,
                         parent=ink)
      oio.put()
      ino.next_invoice_number += 1
      ino.put()
      return oio.key

    self.internal_invoice = _NewInvoiceNumber()
    self.put()

  def __unicode__(self):
    return ' '.join((self.site.get().number, self.site.get().name,
                     self.order_sheet.get().name,
                     '%d items' % self.OrderItems.count(),
                     '$%0.2f' % self.GrandTotal()))

  def CanMakeChanges(self):
    return self.state in ('new', 'Received')

  def VisibleNotes(self):
    if self.notes is None:
      return ''
    return self.notes

  def EstimatedTotal(self):
    if self.sub_total is None:
      return 0.
    t = self.sub_total * (1. + SALES_TAX_RATE)
    return math.ceil(t * 100.) / 100.

  def GrandTotal(self):
    if self.state == 'Deleted':
      return 0.
    if self.actual_total is not None:
      return self.actual_total
    else:
      return self.EstimatedTotal()

  def Total(self):
    return self.GrandTotal()

  def SalesTax(self):
    if self.state == 'Deleted':
      return 0.
    if self.sub_total is None:
      return 0.
    return self.sub_total * SALES_TAX_RATE

  # TODO: seems incorrect to update fulfilled orders.
  def UpdateSubTotal(self):
    """Recomputes sub_total by summing the cost of items and adding tax."""
    sub_total = 0.
    order_items = OrderItem.query(OrderItem.order == self.key)
    for oi in order_items:
      quantity = oi.FloatQuantity()
      if oi.item.get().unit_cost is not None and quantity:
        sub_total += quantity * oi.item.get().unit_cost
    if self.sub_total != sub_total:
      self.sub_total = sub_total
      self.put()
      logging.info('Updated subtotal for order %d to %0.2f',
                   self.key.integer_id(), sub_total)

  def LogisticsStart(self):
    for od in self.orderdelivery_set:
      return "%s (Delivery)" % od.delivery.get().delivery_date
    for od in self.orderpickup_set:
      return "%s (Pickup)" % od.pickup.get().pickup_date
    for od in self.orderretrieval_set:
      return "%s (Drop-off)" % od.retrieval.get().dropoff_date
    return None

  def LogisticsEnd(self):
    for od in self.orderretrieval_set:
      return "%s (Retrieval)" % od.retrieval.get().retrieval_date
    return None

  def LogisticsInstructions(self):
    for od in self.orderdelivery_set:
      return "%s%s %s%s %s" % (
        od.delivery.get().contact and 'Contact ' or '',
        od.delivery.get().contact or '',
        od.delivery.get().contact_phone and 'at ' or '',
        od.delivery.get().contact_phone or '',
        od.delivery.get().notes or '')

    for od in self.orderpickup_set:
      return "%s%s %s%s %s" % (
        od.pickup.get().contact and 'Contact ' or '',
        od.pickup.get().contact or '',
        od.pickup.get().contact_phone and 'at ' or '',
        od.pickup.get().contact_phone or '',
        od.pickup.get().notes or '')

    for od in self.orderretrieval_set:
      return "%s%s %s%s %s" % (
        od.retrieval.get().contact and 'Contact ' or '',
        od.retrieval.get().contact or '',
        od.retrieval.get().contact_phone and 'at ' or '',
        od.retrieval.get().contact_phone or '',
        od.retrieval.get().notes or '')
    return ''

  def UpdateLogistics(self):
    self.logistics_start = self.LogisticsStart()
    self.logistics_end = self.LogisticsEnd()
    self.logistics_instructions = self.LogisticsInstructions()
    self.put()


class OrderItem(SearchableModel):
  """The Items that are in a given Order."""
  item = ndb.KeyProperty(kind=Item)
  order = ndb.KeyProperty(kind=Order)
  supplier = ndb.KeyProperty(kind=Supplier)
  quantity = ndb.IntegerProperty(default=0)
  quantity_float = ndb.FloatProperty(default=0.0)
  name = ndb.StringProperty(default="")

  def FloatQuantity(self):
    """Returns quantity as a float."""
    if self.quantity:
      return float(self.quantity)
    elif self.quantity_float:
      return self.quantity_float
    else:
      return 0.0

  def IsEmpty(self):
    quantity = self.FloatQuantity()
    return not quantity and not self.name

  def SupportsName(self):
    return (self.item.get().supports_extra_name_on_order
            or self.order.get().order_sheet.get().supports_extra_name_on_order)

  def VisibleQuantity(self):
    quantity = self.FloatQuantity()
    if quantity:
      if quantity % 1 == 0:
        return str(int(quantity))
      else:
        return str(quantity)
    else:
      return ''

  def VisibleCost(self):
    quantity = self.FloatQuantity()
    unit_cost = self.item.get().unit_cost
    if quantity and not unit_cost:
      return '0'
    if quantity and unit_cost:
      return '%.2f' % (quantity * unit_cost)
    else:
      return ''


class Delivery(SearchableModel):
  """Delivery to a site (no retrieval)."""
  site = ndb.KeyProperty(kind=NewSite, required=True)
  delivery_date = ndb.StringProperty()
  delivery_date.verbose_name = 'Delivery Date (Mon-Fri only)'
  contact = ndb.StringProperty()
  contact.verbose_name = "Contact person (who will accept delivery)"
  contact_phone = ndb.StringProperty()
  notes = ndb.TextProperty()
  notes.verbose_name = (
    'Instructions for delivery person')


class OrderDelivery(SearchableModel):
  """Maps Order to Delivery."""
  order = ndb.KeyProperty(kind=Order, required=True)
  delivery = ndb.KeyProperty(kind=Delivery, required=True)


class Pickup(SearchableModel):
  """Pick up from RTP warehouse."""
  site = ndb.KeyProperty(kind=NewSite, required=True)
  pickup_date = ndb.StringProperty()
  pickup_date.verbose_name = 'Pickup Date (Mon-Fri only)'
  return_date = ndb.StringProperty()
  return_date.verbose_name = '(Optional) Return date for durable equipment'
  contact = ndb.StringProperty()
  contact.verbose_name = "Contact person (who will pick up)"
  contact_phone = ndb.StringProperty()
  notes = ndb.TextProperty()
  notes.verbose_name = (
    'Instructions for warehouse staff')


class OrderPickup(SearchableModel):
  """Maps Order to Pickup."""
  order = ndb.KeyProperty(kind=Order, required=True)
  pickup = ndb.KeyProperty(kind=Pickup, required=True)


class Retrieval(SearchableModel):
  """Delivery and retrieval to and from a site."""
  site = ndb.KeyProperty(kind=NewSite, required=True)
  dropoff_date = ndb.StringProperty()
  dropoff_date.verbose_name = 'Delivery Date (Mon-Fri only)'
  retrieval_date = ndb.StringProperty()
  retrieval_date.verbose_name = 'Retrieval Date (Mon-Fri only)'
  contact = ndb.StringProperty()
  contact.verbose_name = "Contact person (who will accept delivery)"
  contact_phone = ndb.StringProperty()
  notes = ndb.TextProperty()
  notes.verbose_name = (
    'Instructions for delivery person')


class OrderRetrieval(SearchableModel):
  """Maps Order to Retrieval."""
  order = ndb.KeyProperty(kind=Order, required=True)
  retrieval = ndb.KeyProperty(kind=Retrieval, required=True)


class InventoryItem(SearchableModel):
  """The Items that are in the inventory."""
  item = ndb.KeyProperty(kind=Item)
  quantity = ndb.IntegerProperty(default=0)
  quantity_float = ndb.FloatProperty(default=0.0)
  location = ndb.StringProperty()
  available_on = ndb.DateProperty()
  last_editor = ndb.UserProperty()
  modified = ndb.DateTimeProperty(auto_now=True)


def _GetRateFromArray(default, array, activity_date):
  if not array:
    return default
  activity_date_str = activity_date.isoformat()
  rate = default
  for dr in sorted(s.split() for s in array):
    if activity_date_str < dr[0]:
      break
    rate = float(dr[1])
  return rate


class StaffPosition(SearchableModel):
  """Staff positions that have hourly billing."""
  position_name = ndb.StringProperty()

  # Defaults possibly superceded by the date-based lists below, and destined to be deprecated once
  # all objects have moved to the date-based lists.
  hourly_rate = ndb.FloatProperty(default=0.0)
  mileage_rate = ndb.FloatProperty(default=0.0)

  # Space-separated pairs of date and rate strings, to support
  # rates that change over time. The scheme here is to list the effective date of rate changes,
  # along with the new rate.

  # These are entered in the datastore editor as
  # type=Array and a value formatted like
  # {
  #   "values": [
  #     {
  #       "stringValue": "2016-01-01 10.0"
  #     },
  #     {
  #       "stringValue": "2017-01-01 20.0"
  #     }
  #   ]
  # }
  # Then the values appear here as unicode strings:
  # [u'2016-01-01 10.0', u'2017-01-01 20.0']
  hourly_rate_after_date = ndb.StringProperty(repeated=True)
  mileage_rate_after_date = ndb.StringProperty(repeated=True)

  last_editor = ndb.UserProperty()
  modified = ndb.DateTimeProperty(auto_now=True)

  def GetHourlyRate(self, activity_date):
    return _GetRateFromArray(self.hourly_rate, self.hourly_rate_after_date, activity_date)

  def GetMileageRate(self, activity_date):
    return _GetRateFromArray(self.mileage_rate, self.mileage_rate_after_date, activity_date)

  def __unicode__(self):
    return '%s' % self.position_name

  def __str__(self):
    return '%s' % self.position_name


class CheckRequest(SearchableModel):
  """A Check Request is a request for reimbursement."""
  site = ndb.KeyProperty(kind=NewSite)
  captain = ndb.KeyProperty(kind=Captain)
  program = ndb.StringProperty()
  payment_date = ndb.DateProperty()
  labor_amount = ndb.FloatProperty(default=0.0)
  labor_amount.verbose_name = 'Labor Amount ($)'
  materials_amount = ndb.FloatProperty(default=0.0)
  materials_amount.verbose_name = 'Materials Amount ($)'
  food_amount = ndb.FloatProperty(default=0.0)
  food_amount.verbose_name = 'Food Amount ($)'
  description = ndb.TextProperty()
  name = ndb.StringProperty()
  name.verbose_name = 'Payable To'
  address = ndb.TextProperty()
  address.verbose_name = "Payee Address"
  tax_id = ndb.StringProperty()
  tax_id.verbose_name = "Payee Tax ID"
  form_of_business = ndb.StringProperty(
    choices=('Corporation', 'Partnership', 'Sole Proprietor',
             'Don\'t Know'))
  form_of_business.verbose_name = "Payee Business Type"
  state = ndb.StringProperty()
  last_editor = ndb.UserProperty(auto_current_user=True)
  modified = ndb.DateTimeProperty(auto_now=True)

  def put(self, *a, **k):
    self.program = self.site.get().program
    me = super(CheckRequest, self).put(*a, **k)
    self.site.get().RecomputeExpenses()
    return me

  def Total(self):
    return self.labor_amount + self.materials_amount + self.food_amount


class VendorReceipt(SearchableModel):
  """A Vendor Receipt is a report of a purchase outside of ROOMS."""
  site = ndb.KeyProperty(kind=NewSite)
  captain = ndb.KeyProperty(kind=Captain)
  program = ndb.StringProperty()
  purchase_date = ndb.DateProperty()
  vendor = ndb.StringProperty()
  supplier = ndb.KeyProperty(kind=Supplier)
  amount = ndb.FloatProperty()
  amount.verbose_name = 'Purchase Amount ($)'
  description = ndb.TextProperty()
  state = ndb.StringProperty()
  last_editor = ndb.UserProperty()
  modified = ndb.DateTimeProperty(auto_now=True)

  @property
  def name(self):
    if self.supplier:
      return self.supplier.get().name
    return self.vendor

  def put(self, *a, **k):
    self.program = self.site.get().program
    me = super(VendorReceipt, self).put(*a, **k)
    self.site.get().RecomputeExpenses()
    return me

  def Total(self):
    return self.amount or 0


class InKindDonation(SearchableModel):
  """An In-kind donation to a site."""
  site = ndb.KeyProperty(kind=NewSite)
  captain = ndb.KeyProperty(kind=Captain)
  program = ndb.StringProperty()
  donation_date = ndb.DateProperty()
  donor = ndb.StringProperty()
  donor_phone = ndb.StringProperty()
  donor_info = ndb.TextProperty()
  donor_info.verbose_name = (
    'Include as much of the following donor information as possible:'
    ' donor name, company, address, phone, email.')
  labor_amount = ndb.FloatProperty(default=0.0)
  labor_amount.verbose_name = 'Labor Value ($)'
  materials_amount = ndb.FloatProperty(default=0.0)
  materials_amount.verbose_name = 'Materials Value ($)'
  description = ndb.TextProperty()
  budget = ndb.StringProperty(choices=('Normal', 'Roofing'), default='Normal')
  state = ndb.StringProperty()
  last_editor = ndb.UserProperty()
  modified = ndb.DateTimeProperty(auto_now=True)

  @property
  def name(self):
    return self.donor

  def put(self, *a, **k):
    self.program = self.site.get().program
    me = super(InKindDonation, self).put(*a, **k)
    self.site.get().RecomputeExpenses()
    return me

  def Total(self):
    return self.labor_amount + self.materials_amount


class StaffTime(SearchableModel):
  """Expense type that represents hourly staff time."""
  site = ndb.KeyProperty(kind=NewSite, required=True)
  captain = ndb.KeyProperty(kind=Captain)
  position = ndb.KeyProperty(kind=StaffPosition)
  program = ndb.StringProperty()
  state = ndb.StringProperty()
  hours = ndb.FloatProperty(default=0.0)
  hours.verbose_name = 'Hours'
  miles = ndb.FloatProperty(default=0.0)
  miles.verbose_name = 'Miles'
  activity_date = ndb.DateProperty()
  description = ndb.TextProperty()
  last_editor = ndb.UserProperty(auto_current_user=True)
  modified = ndb.DateTimeProperty(auto_now=True)

  def put(self, *a, **k):
    self.program = self.site.get().program
    me = super(StaffTime, self).put(*a, **k)
    self.site.get().RecomputeExpenses()
    return me

  @property
  def name(self):
    return self.position

  def HoursTotal(self):
    if not self.position:
      logging.warning('empty position %s', str(self))
    if self.state in ('new', 'deleted'):
      return 0.0
    if self.hours is None:
      self.hours = 0.0
    return self.hours * self.position.get().GetHourlyRate(self.activity_date)

  def MileageTotal(self):
    if not self.position:
      logging.warning('empty position %s', str(self))
    if self.state in ('new', 'deleted'):
      return 0.0
    if self.miles is None:
      self.miles = 0.0
    return self.miles * self.position.get().GetMileageRate(self.activity_date)

  def Total(self):
    return self.HoursTotal() + self.MileageTotal()


# I think this can be removed.  There is a template and view called "Expense"
# but I don't see anything that references this model.   And there are no
# entities in the prod datastore.
class Expense(SearchableModel):
  """A generic expense."""
  payee = ndb.KeyProperty(kind=Supplier)
  action = ndb.StringProperty(choices=('on account', 'need reimbursement'))

  site = ndb.KeyProperty(kind=NewSite)
  captain = ndb.KeyProperty(kind=Captain)
  program = ndb.StringProperty()
  date = ndb.DateProperty()
  amount = ndb.FloatProperty()
  amount.verbose_name = 'Purchase Amount ($)'
  description = ndb.TextProperty()
  state = ndb.StringProperty()
  last_editor = ndb.UserProperty()
  modified = ndb.DateTimeProperty(auto_now=True)


def get_all_searchable_models():
  searchable_models = general_utils.get_all_subclasses(SearchableModel)
  searchable_models.sort(key=lambda m: m.get_search_order())
  return searchable_models


def model_from_search_document(doc):
  name_to_model_type_map = {m.__name__: m for m in get_all_searchable_models()}
  key_ids = doc['model_key_id']
  assert len(key_ids) == 1
  model_type_names = doc['model_name']
  assert len(model_type_names) == 1
  model_type = name_to_model_type_map.get(model_type_names[0].value)
  assert model_type is not None
  return model_type.get_by_id(int(key_ids[0].value))