"""Staff views"""

import datetime
import json
import logging
import webapp2
from google.appengine.ext import ndb

import ndb_models
import common

TEST_SITE_NUMBER = '11999ZZZ'


class SelectProgram(webapp2.RequestHandler):
  """Handler for Staff to select a program.

  This is different from other Staff handlers because it is 
  the only prerequisite to loading the StaffHome page.  So 
  it requires that the user is staff but does not require that 
  program is already selected. Bootstrapping.
  """

  def get(self):
    user, _ = common.GetUser(self.request)
    if not user and not user.staff:
      return webapp2.redirect_to('Start')
    program = self.request.get('program')
    if not program:
      what_you_are_doing = "Select a Program to work on"
      program_url_base = webapp2.uri_for('SelectProgram')
      return common.Respond(self.request, 'select_program', locals())

    if program not in common.PROGRAMS:
      return http.HttpResponseError('program %s not in PROGRAMS' % program)
    user.staff.program_selected = program
    user.staff.put()
    return webapp2.redirect_to('StaffHome')


class StaffHandler(webapp2.RequestHandler):
  """Handler base class that ensures the user meets Staff view prerequisites:
  - user is logged in
  - user matches an existing Staff record
  - Staff record has a selected Program
  """
  def dispatch(self, *a, **k):
    user, status = common.GetUser(self.request)
    if user and user.staff:    
      if not user.staff.program_selected:
        logging.info(self.request)
        return webapp2.redirect_to('SelectProgram')
      super(StaffHandler, self).dispatch(*a, **k)
    else:
      return webapp2.redirect_to('Start')

    
class StaffHome(StaffHandler):
  def get(self):
    order_sheets = list(ndb_models.OrderSheet.query())
    order_sheets.sort(key=lambda x: x.name)
    jurisdictions = list(ndb_models.Jurisdiction.query())
    jurisdictions.sort(key=lambda x: x.name)
    d = {'order_sheets': order_sheets,
         'test_site_number': TEST_SITE_NUMBER,
         'jurisdictions': jurisdictions,
         }
    return common.Respond(self.request, 'staff_home', d)


class SiteScopeOfWork(StaffHandler):
  def post(self, id):
    """Updates a Site's scope_of_work field."""
    obj = ndb.Key(ndb_models.NewSite, int(id)).get()
    if not obj:
      webapp2.abort(404)
    field = self.request.POST['id']
    if not field:
      return webapp2.abort(400)
    value = self.request.POST['value']
    setattr(obj, field, value)
    obj.put()
    self.response.write(value)

  
class AutocompleteHandler(StaffHandler):
  model_class = None
  program_filter = False

  def get(self):
    prefix = str(self.request.get('term').lower())
    logging.info(prefix)
    items = self.model_class.query(self.model_class.search_prefixes == prefix)
    if self.program_filter:
      user, _ = common.GetUser(self.request)
      items = items.filter(self.model_class.program == user.program_selected)
    matches = {}
    for i in items.iter():
      label = i.Label()
      matches[label] = str(i.key.integer_id())

    self.response.content_type='application/json'
    self.response.write(json.dumps(matches))


class SiteAutocomplete(AutocompleteHandler):
  """Return JSON to autocomplete a Site ID based on a prefix."""
  model_class = ndb_models.NewSite
  program_filter = True


class CaptainAutocomplete(AutocompleteHandler):
  """Return JSON to autocomplete a Captain."""
  model_class = ndb_models.Captain
  program_filter = False


class SiteView(StaffHandler):
  def get(self, id=None):
    if id:
      id = int(id)
      site = ndb.Key(ndb_models.NewSite, id).get()
    d = dict(
      map_width=common.MAP_WIDTH, map_height=common.MAP_HEIGHT
    )
    entries = [site]
    d['site_list_detail'] = True
    d['start_new_order_submit'] = common.START_NEW_ORDER_SUBMIT
    d['entries'] = entries
    order_sheets = ndb_models.OrderSheet.query().order(ndb_models.OrderSheet.name)
    d['order_sheets'] = order_sheets
    return common.Respond(self.request, 'site_list_one', d)


class SiteExpenses(StaffHandler):
  def get(self, id=None):
    id = int(id)
    site = ndb.Key(ndb_models.NewSite, id).get()
    return common.Respond(self.request, 'site_expenses', {'site': site})


class SiteSummary(StaffHandler):
  def get(self, id=None):
    id = int(id)
    site = ndb.Key(ndb_models.NewSite, id).get()
    return common.Respond(self.request, 'site_summary', {'site': site})

  
SITE_EXPENSE_TYPES = dict((c.__name__, c) for c in (
    ndb_models.CheckRequest,
    ndb_models.VendorReceipt,
    ndb_models.InKindDonation,
    ndb_models.StaffTime,
))
  
class SiteExpenseState(StaffHandler):
  def get(self, item_cls, item_id):
    """Updates a site expense's state field."""
    user, _ = common.GetUser(self.request)
    if not user.staff:
      return webapp2.abort(403)
    if not request.POST:
      return webapp2.abort(400)
    cls = SITE_EXPENSE_TYPES[item_cls]
    modl = ndb.Key(cls, int(item_id))
    if not modl:
      return webapp2.abort(404)
    value = request.POST['value']
    modl.state = value
    modl.put()
    return self.request

  

class SitesAndCaptains(StaffHandler):
  """Show all Sites and their associated captains in a big list"""
  def get(self):
    user, _ = common.GetUser(self.request)
    if not user.program_selected:
      webapp2.abort(400)
    query = ndb_models.NewSite.query(ndb_models.NewSite.program == user.program_selected)
    query.order(ndb_models.NewSite.number)
    entries = list(query)
    logging.info('loaded %d sites for %s', len(entries), user.program_selected)
    sitecaptains_by_site = {}
    # TODO: this is fetching too many - we only need those for the current
    # program.  use ancestor?
    for sc in ndb_models.SiteCaptain.query():
      sitecaptains_by_site.setdefault(sc.site.integer_id(), []).append(sc)
    logging.info('loaded sitecaptains')
    for s in entries:
      k = s.key.integer_id()
      if k in sitecaptains_by_site:
        s.sitecaptains = sitecaptains_by_site[k]
    d = {'entries': entries, 'num_entries': len(entries), 'user': user,
         'sitecaptains_by_site': sitecaptains_by_site}
    return common.Respond(self.request, 'site_list', d)

    
def _EntryList(request, model_cls, template, params=None, query=None):
  """Generic helper method to perform a list view.

  This method does not enforce any authorization. It should be called after 
  authorization is successful..

  Template should iterate over a list called 'entries'.
  Sorts entries on their 'name' attribute (which they must have).

  Args:
    request: the request object
    model_cls: the class of model, like models.Captain
    template: name of template file, like 'captain_list'
    params: dict of more template parameters
    query: db.Query object to use, if not model_cls.query()
    """
  if query is None:
    query = model_cls.query()
  entries = list(query)
  entries.sort(key=lambda x: x.name)
  d = {'entries': entries, 'num_entries': len(entries),
       'cls': model_cls,
       'model_cls_name': model_cls.__name__}
  if params:
    d.update(params)
  return common.Respond(request, template, d)


class EditView(StaffHandler):
  model_class = None
  template_value = None
  template_file = None

  def get(self, id=None):
    d = dict(list_uri=webapp2.uri_for(self.list_view),
             type=self.template_value)
    if id:
      id = int(id)
      d[self.template_value] = ndb.Key(self.model_class, id).get()
    return common.Respond(self.request, self.template_file, d)
  

class StaffList(StaffHandler):
  def get(self):
    return _EntryList(self.request, ndb_models.Staff, 'staff_list')

class Staff(EditView):
  model_class = ndb_models.Staff
  list_view = 'StaffList'
  template_value = 'staff'
  template_file = 'simple_form'


class CaptainList(StaffHandler):
  def get(self):
    return _EntryList(self.request, ndb_models.Captain, 'captain_list')

class Captain(EditView):
  model_class = ndb_models.Captain
  list_view = 'CaptainList'
  template_value = 'captain'
  template_file = 'simple_form'
  

class SupplierList(StaffHandler):
  def get(self):
    return _EntryList(self.request, ndb_models.Supplier, 'supplier_list')

class Supplier(EditView):
  model_class = ndb_models.Supplier
  list_view = 'SupplierList'
  template_value = 'supplier'
  template_file = 'simple_form'

  
# SiteList is done by custom view SitesAndCaptains

class Site(EditView):
  model_class = ndb_models.NewSite
  list_view = 'SitesAndCaptains'
  template_value = 'site'
  template_file = 'simple_form'

  
class OrderSheetList(StaffHandler):
  def get(self):
    return _EntryList(self.request, ndb_models.OrderSheet, 'ordersheet_list')

class OrderSheet(EditView):
  model_class = ndb_models.OrderSheet
  list_view = 'OrderSheetList'
  template_value = 'ordersheet'
  template_file = 'simple_form'


class SiteExpenseList(StaffHandler):
  model_class = None   # 'StaffTime'
  expense_type = None  # 'Staff Time'
  table_template = None # 'stafftime_table.html'
  
  def get(self, site_id=None):
    mdl_cls = getattr(ndb_models, self.model_class)
    query = mdl_cls.query(mdl_cls.state != 'new')
    params = {'which_site': 'All',
              'expense_type': self.expense_type,
              'model_cls_name': self.model_class,
              'table_template': self.table_template}
    if site_id is not None:
      site_key = ndb.Key(ndb_models.NewSite, int(site_id))
      site = site_key.get()
      query = query.filter(mdl_cls.site == site_key)
      params['which_site'] = 'Site ' + site.number
    else:
      user, _ = common.GetUser(self.request)
      if user.program_selected:
        query = query.filter(mdl_cls.program == user.program_selected)
    logging.info('found %d orders for %s', query.count(), query)
    return _EntryList(self.request, mdl_cls, 'site_expense_list',
                      params=params, query=query)


class SiteExpenseEditor(StaffHandler):
  model_class = None
  template_value = None
  template_file = None

  def get(self, site_id, id=None):
    site = ndb.Key(ndb_models.NewSite, int(site_id)).get()
    d = dict(list_uri=webapp2.uri_for(self.list_view, site_id=site_id),
             site=site,
             type=self.template_value)
    if id:
      id = int(id)
      d[self.template_value] = ndb.Key(self.model_class, id).get()
    else:
      d[self.template_value] = self.model_class(site=site.key)
    return common.Respond(self.request, self.template_file, d)


class StaffTimeList(SiteExpenseList):
  model_class = 'StaffTime'
  expense_type = 'Staff Time'
  table_template = 'stafftime_table.html'


class StaffTimeView(StaffHandler):
  def get(self, id):
    """Printable static view of an expense."""
    entity = ndb.Key(ndb_models.StaffTime, int(id)).get()
    return common.Respond(self.request, 'stafftime_view',
                          {'entity': entity})

  
class StaffTime(SiteExpenseEditor):
  model_class = ndb_models.StaffTime
  list_view = 'StaffTimeBySite'
  template_value = 'Staff Time'
  template_file = 'expense_form'


class CheckRequestList(SiteExpenseList):
  model_class = 'CheckRequest'
  expense_type = 'Check Request'
  table_template = 'checkrequest_table.html'


class CheckRequestView(StaffHandler):
  def get(self, id):
    entity = ndb.Key(ndb_models.CheckRequest, int(id)).get()
    return common.Respond(self.request, 'checkrequest_view',
        {'entity': entity})

  
class CheckRequest(SiteExpenseEditor):
  model_class = ndb_models.CheckRequest
  list_view = 'CheckRequestBySite'
  template_value = 'Check Request'
  template_file = 'expense_form'


class VendorReceiptList(SiteExpenseList):
  model_class = 'VendorReceipt'
  expense_type = 'Vendor Receipt'
  table_template = 'vendorreceipt_table.html'

  
class VendorReceiptView(StaffHandler):
  def get(self, id):
    entity = ndb.Key(ndb_models.VendorReceipt, int(id)).get()
    return common.Respond(self.request, 'vendorreceipt_view',
        {'entity': entity}
)

  
class VendorReceipt(SiteExpenseEditor):
  model_class = ndb_models.VendorReceipt
  list_view = 'VendorReceiptBySite'
  template_value = 'Vendor Receipt'
  template_file = 'expense_form'


class InKindDonationList(SiteExpenseList):
  model_class = 'InKindDonation'
  expense_type = 'In-Kind Donation'
  table_template = 'inkinddonation_table.html'

class InKindDonationView(StaffHandler):
  def get(self, id):
    entity = ndb.Key(ndb_models.InKindDonation, int(id)).get()
    return common.Respond(self.request, 'inkinddonation_view',
        {'entity': entity}
)

class InKindDonation(SiteExpenseEditor):
  model_class = ndb_models.InKindDonation
  list_view = 'InKindDonationBySite'
  template_value = 'In-Kind Donation'
  template_file = 'expense_form'

def _SortOrderItemsWithSections(order_items):
  order_items.sort(
      key=lambda x: (x.item.get().order_form_section or None, x.item.get().name))
  prev_section = None
  for o in order_items:
    new_section = o.item.get().order_form_section or None
    if prev_section != new_section:
      o.first_in_section = True
    prev_section = new_section

    
class OrderChooseForm(StaffHandler):
  def get(self, site_id):
    site = ndb.Key(ndb_models.NewSite, int(site_id)).get()
    existing_orders = {}
    query = site.Orders.Items()
    for order in query:
      os = order.order_sheet.get()
      if os.code not in existing_orders:
        existing_orders[os.code] = []
        existing_orders[os.code].append(order)

    order_sheets = ndb_models.OrderSheet.query().order(ndb_models.OrderSheet.name)
    order_sheets = [o for o in order_sheets if o.visibility != 'Staff Only']
    for os in order_sheets:
      order_items = [ndb_models.OrderItem(item=i.key) for i in os.item_set]
      _SortOrderItemsWithSections(order_items)
      os.sorted_items = order_items[:]
      os.num_existing_orders = 0
      if os.code in existing_orders:
        os.existing_orders = existing_orders[os.code]
        os.num_existing_orders = len(existing_orders[os.code])

    t = {'order_sheets': order_sheets,
         'site': site}
    return common.Respond(self.request, 'order_preview', t)



class OrderList(SiteExpenseList):
  model_class = 'Order'
  expense_type = 'Order'
  table_template = 'order_table.html'

class OrderView(StaffHandler):
  def get(self, order_id):
    order = models.Order.get_by_id(int(order_id))
    q = models.OrderItem.all().filter('order = ', order)
    order_items = [oi for oi in q if oi.FloatQuantity()]
    _SortOrderItemsWithSections(order_items)
    d = {'orders': [{'order': order,
                     'order_items': order_items}],
         'action_verb': 'Review',
         'show_logistics_details': True,
    }
    return common.Respond(request, 'order_fulfill', d)

class Order(SiteExpenseEditor):
  model_class = ndb_models.Order
  list_view = 'OrderBySite'
  template_value = 'Order'
  template_file = 'expense_form'
            

class ItemList(StaffHandler):
  def get(self):
    return _EntryList(self.request, ndb_models.Item, 'item_list')

class Item(EditView):
  model_class = ndb_models.Item
  list_view = 'ItemList'
  template_value = 'item'
  template_file = 'simple_form'

  
"""
class ExampleList(StaffHandler):
  def get(self):
    return _EntryList(self.request, ndb_models.Example, 'example_list')

class Example(EditView):
  model_class = ndb_models.Example
  list_view = 'ExampleList'
  template_value = 'example'
  template_file = 'simple_form'
"""
  


