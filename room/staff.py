"""Staff views"""

import csv
import datetime
import json
import logging
import webapp2
from google.appengine.ext import ndb

import ndb_models
import common

TEST_SITE_NUMBER = '11999ZZZ'
EXPORT_CSV = 'Export CSV'
POSTED_ID_PREFIX = 'export_'


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


class SiteBudget(StaffHandler):
  """List all Sites with a "Budget" view."""
  def get(self):
    user, _ = common.GetUser(self.request)
    params = {
        'export_csv': EXPORT_CSV,
        'export_checkbox_prefix': POSTED_ID_PREFIX
    }
    query = ndb_models.NewSite.query(ndb_models.NewSite.program == user.staff.program_selected)
    params['program'] = user.staff.program_selected

    # this 'q' param is just for testing
    if 'q' in self.request.GET:
      query = query.filter(ndb_models.NewSite.search_prefixes == self.request.GET['q'].lower())
      params['search'] = self.request.GET['q']

    params['jurisdiction'] = self.request.GET.get('j')
    if params['jurisdiction']:
      query = query.filter(ndb_models.NewSite.jurisdiction == params['jurisdiction'])

    entries = list(query)
    total = 0
    for site in entries:
      total += site.Expenses()

    params.update({'entries': entries, 'num_entries': len(entries), 'user': user,
                   'total_expenses': total})
    return common.Respond(self.request, 'site_budget', params)


class SiteBudgetExport(StaffHandler):
  def post(self):
    """Export Site budget rows as CSV."""
    user, _ = common.GetUser(self.request)
    if self.request.POST['submit'] == EXPORT_CSV:
      self.response.content_type = 'text/csv'
      self.response.headers['Content-Disposition'] = (
          'attachment; filename=%s_site_budget.csv' % user.email())
      _SiteBudgetExportInternal(self.response, self.request.POST)
      return self.response

def PostedIds(post_vars):
  """Extract IDs from post_vars."""
  site_ids = []
  for var in post_vars:
    if var.startswith(POSTED_ID_PREFIX):
      site_ids.append(int(var[len(POSTED_ID_PREFIX):]))
  return site_ids
  
def _SiteBudgetExportInternal(writable, post_vars):
  """Write site budget rows as CSV to a file-like object."""
  site_ids = PostedIds(post_vars)
  site_keys = list(ndb.Key(ndb_models.NewSite, id) for id in site_ids)
  sites = list(site for site in ndb.get_multi(site_keys) if site)
  sites.sort(key=lambda o: o.number)
  writer = csv.writer(writable)
  # These should be similar to the columns in the site_budget.html template.
  writer.writerow(['Site Number',
                   'Name',
                   'Sponsor',
                   '$ Budget',
                   '$ Balance',
                   '$ Total Expenses',
                   '$ Orders',
                   '$ Check Requests',
                   '$ Vendor Receipts',
                   '$ In-Kind Donations',
                   '$ Staff Time',
                   ])
  for s in sites:
    row = [s.number,
           s.name,
           s.sponsor,
           s.budget,
           s.BudgetRemaining(),
           s.Expenses(),
           s.order_total,
           s.CheckRequestTotal(),
           s.VendorReceiptTotal(),
           s.InKindDonationTotal(),
           s.StaffTimeTotal(),
           ]
    row = [unicode(f).encode('ascii', 'ignore') for f in row]
    writer.writerow(row)


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
  if not entries:
    webapp2.abort(404)
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
  template_file = 'site'

  
class OrderSheetList(StaffHandler):
  def get(self):
    return _EntryList(self.request, ndb_models.OrderSheet, 'ordersheet_list')

class OrderSheet(EditView):
  model_class = ndb_models.OrderSheet
  list_view = 'OrderSheetList'
  template_value = 'ordersheet'
  template_file = 'simple_form'

class OrderSheetItemList(StaffHandler):
  """Request / -- show all items in an Order Sheet."""
  def get(self, id):
    sheet = ndb.Key(ndb_models.OrderSheet, int(id)).get()
    return _EntryList(self.request, ndb_models.Item, 'order_sheet_item_list',
                      query=sheet.item_set, params={'order_sheet': sheet})

class SiteExpenseList(StaffHandler):
  model_class = None   # 'StaffTime'
  expense_type = None  # 'Staff Time'
  table_template = None # 'stafftime_table.html'
  
  def get(self, site_id=None):
    mdl_cls = getattr(ndb_models, self.model_class)
    query = mdl_cls.query()
    query = query.filter(mdl_cls.state != 'Deleted')
    params = {
      'which_site': 'All',
      'expense_type': self.expense_type,
      'model_cls_name': self.model_class,
      'table_template': self.table_template,
    }
    if site_id is not None:
      site_key = ndb.Key(ndb_models.NewSite, int(site_id))
      site = site_key.get()
      query = query.filter(mdl_cls.site == site_key)
      params['which_site'] = 'Site ' + site.number
      params['next_key'] = site_key.urlsafe()
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
  template_value = 'checkrequest'
  template_file = 'checkrequest'


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


# This is a super lame list function, there is a better one at OrderPicklist
class OrderList(SiteExpenseList):
  model_class = 'Order'
  expense_type = 'Order'
  table_template = 'order_table.html'

  
class OrderView(StaffHandler):
  def get(self, id):
    order = ndb.Key(ndb_models.Order, int(id)).get()
    order.UpdateSubTotal()
    q = ndb_models.OrderItem.query(ndb_models.OrderItem.order == order.key)
    order_items = [oi for oi in q if oi.FloatQuantity()]
    _SortOrderItemsWithSections(order_items)
    d = {'order': order,
         'order_items': order_items,
         'site': order.site.get(),
         'order_sheet': order.order_sheet.get(),
         'action_verb': 'Review',
         'sales_tax_pct': ndb_models.SALES_TAX_RATE * 100.,
         'show_instructions': True,
         'show_logistics_details': True,
    }
    return common.Respond(self.request, 'order_view', d)

class OrderFlow(StaffHandler):
  def get(self, site_id, id=None):
    site = ndb.Key(ndb_models.NewSite, int(site_id)).get()
    d = dict(site=site)
    return common.Respond(self.request, 'order_flow', d)


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
  


###############
# Order stuff #
###############

FULFILL_MULTIPLE = 'Fulfill Multiple Orders'

class OrderPicklist(StaffHandler):
  def get(self):
    """Request / -- show all orders."""
    user, _ = common.GetUser(self.request)
    program = user.program_selected
    query = ndb_models.Order.query(
      ndb_models.Order.state != 'Deleted',
      ndb_models.Order.state != 'new')
    if program is not None:
      query = query.filter(ndb_models.Order.program == program)
    next_key = ''
    order_sheet = None
    order_sheet_id = self.request.get('order_sheet_id')
    if order_sheet_id:
      order_sheet = ndb.Key(ndb_models.OrderSheet, int(order_sheet_id)).get()
      if order_sheet is not None:
        query = query.filter(ndb_models.Order.order_sheet == order_sheet.key)
        next_key = order_sheet.key.urlsafe()
    orders = list(query)
    mass_action = {'export_csv': EXPORT_CSV,
                   'fulfill_many': FULFILL_MULTIPLE}
    d = {
      'entries': orders,
      'order_sheet': order_sheet,
      'export_checkbox_prefix': POSTED_ID_PREFIX,
      'mass_action': mass_action,
      'next_key': next_key,
      'num_being_filled': len([o for o in orders
                               if o.state == 'Being Filled'])
    }
    return common.Respond(self.request, 'order_list', d)


class _OrderChangeConfirm(StaffHandler):
  state = None  # abstract base class

  def post(self):
    order_ids = PostedIds(self.request.POST)
    order_keys = (ndb.Key(ndb_models.Order, order_id) for order_id in order_ids)
    orders = ndb.get_multi(order_keys)
    for order in orders:
      order.state = self.state
    ndb.put_multi(orders)

    next_key = self.request.get('next_key')
    if next_key is not None:
      k = ndb.Key(urlsafe=next_key)
      if k.kind() == 'NewSite':
        return self.redirect_to('OrderBySite', site_id=k.id())
      elif k.kind() == 'OrderSheet':
        return self.redirect_to('OrderByProgram', order_sheet_id=k.id())
      else:
        logging.warn('no plan for continuing to list of orders for kind: {}'.format(k.kind()))

    # fallback
    return webapp2.redirect_to('OrderByProgram')  # TODO: should go somewhere better.
  

class OrderDeleteConfirm(_OrderChangeConfirm):
  state = 'Deleted'

class OrderFulfillConfirm(_OrderChangeConfirm):
  state = 'Being Filled'


class _OrderFulfillInternal(StaffHandler):
  options = None  # abstract base

  def get(self, order_id):
    next_key = self.request.get('next_key')
    order_ids = [order_id]
    orders = []
    for order_id in order_ids:
      order = ndb.Key(ndb_models.Order, int(order_id)).get()
      q = ndb_models.OrderItem.query().filter(ndb_models.OrderItem.order == order.key)
      order_items = [oi for oi in q if oi.FloatQuantity()]
      _SortOrderItemsWithSections(order_items)
      orders.append({'order': order,
                     'order_items': order_items})


    list_url = webapp2.uri_for('OrderBySheet',  # TODO: better list url
                               next_key=next_key)
    confirm_url = webapp2.uri_for(self.options['confirm_method'], next_key=next_key)

    orders.sort(key=lambda o: o['order'].site.get().number)
    d = {
      'orders': orders,
      'order_items': order_items,
      'back_to_list_url': list_url,
      'confirm_url': confirm_url,
      'action_verb': self.options['action_verb'],
      'submit_value': self.options['submit_value'],
      'should_print': self.options['should_print'],
      'show_logistics_details': True,
      'num_orders': len(orders),
      'export_checkbox_prefix':
      POSTED_ID_PREFIX,
    }
    return common.Respond(self.request, 'order_fulfill', d)

  
class OrderDelete(_OrderFulfillInternal):
  """Prompt user to delete the order."""
  options = {
    'action_verb': 'Delete',
    'confirm_method': 'OrderDeleteConfirm',
    # TODO: purists insist that UI text be in templates.
    'submit_value': 'Click here to confirm deletion',  
    'should_print': False,
  }
  
  
class OrderFulfill(_OrderFulfillInternal):
  """Start the fulfillment process for an order."""
  options = {
    'action_verb': 'Fulfill',
    'confirm_method': 'OrderFulfillConfirm',
    'submit_value': 'Click here to print and confirm fulfillment has started',
    'should_print': True,
  }
