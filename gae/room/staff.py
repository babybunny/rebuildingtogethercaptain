"""Staff views"""

import csv
import datetime
import json
import logging
import collections
import traceback
import urllib

import webapp2
from google.appengine.ext import ndb
from google.appengine.api import search
from google.appengine.ext.blobstore import blobstore
from google.appengine.ext.webapp import blobstore_handlers

import common
import ndb_models
import general_utils

TEST_SITE_NUMBER = '11999ZZZ'
EXPORT_CSV = 'Export CSV'
POSTED_ID_PREFIX = 'export_'


def send_message_with_status(response, message, status=500):
  if status > 399:
    logging.error(message)
  response.set_status(404)
  response.write(message)



class SelectProgram(webapp2.RequestHandler):
  """Handler for Staff to select a program.

  This is different from other Staff handlers because it is
  the only prerequisite to loading the StaffHome page.  So
  it requires that the user is staff but does not require that
  program is already selected. Bootstrapping.
  """

  def get(self):
    user = common.RoomsUser.from_request(self.request)
    if not user and not user.staff:
      return webapp2.redirect_to('Start')
    program_key_id = self.request.get('program_key_id')
    if not program_key_id:
      what_you_are_doing = "Select a Program to work on"
      program_url_base = webapp2.uri_for('SelectProgram')
      return common.Respond(self.request, 'select_program', locals())
    program = ndb_models.Program.get_by_id(int(program_key_id))
    user.staff.program_selected = program.name
    user.staff.program_selected_key = program.key
    user.staff.put()
    return webapp2.redirect_to('StaffHome')


class StaffHandler(webapp2.RequestHandler):
  """Handler base class that ensures the user meets Staff view prerequisites:
  - user is logged in
  - user matches an existing Staff record
  - Staff record has a selected Program
  """

  model_class = None
  searchable_model_class = None

  def dispatch(self, *a, **k):
    user = common.RoomsUser.from_request(self.request)
    if user and user.staff:
      if not user.staff.program_selected:
        logging.info(self.request)
        return webapp2.redirect_to('SelectProgram')
      super(StaffHandler, self).dispatch(*a, **k)
    else:
      return webapp2.redirect_to('Start')


class StaffOrCaptainHandler(webapp2.RequestHandler):
  """Handler base class that ensures the user meets Staff or Captain view prerequisites:
  - user is logged in
  - user matches an existing Staff record OR user matches an existing Captian record
  - if Staff, record has a selected Program
  """

  model_class = None
  searchable_model_class = None

  def dispatch(self, *a, **k):
    user = common.RoomsUser.from_request(self.request)
    if not user:
      return webapp2.redirect_to('Start')
    if user.staff:
      if not user.staff.program_selected:
        logging.info(self.request)
        return webapp2.redirect_to('SelectProgram')
      super(StaffOrCaptainHandler, self).dispatch(*a, **k)
    elif user.captain:
      super(StaffOrCaptainHandler, self).dispatch(*a, **k)
    else:
      return webapp2.redirect_to('Start')


class StaffHome(StaffHandler):
  def get(self):
    order_sheets = list(ndb_models.OrderSheet.query())
    order_sheets.sort(key=lambda x: x.name)
    jurisdictions = list(ndb_models.Jurisdiction.query())
    jurisdictions.sort(key=lambda x: x.name)
    d = {
      'order_sheets': order_sheets,
      'test_site_number': TEST_SITE_NUMBER,
      'jurisdictions': jurisdictions
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

  program_filter = False

  def get(self):
    prefix = str(self.request.get('term').lower())
    items = self.model_class.query(self.model_class.search_prefixes == prefix)
    if self.program_filter:
      user = common.RoomsUser.from_request(self.request)
      items = items.filter(self.model_class.program == user.program_selected)
    matches = {}
    for i in items.iter():
      label = i.Label()
      matches[label] = str(i.key.integer_id())

    self.response.content_type = 'application/json'
    self.response.write(json.dumps(matches))


class SiteAutocomplete(AutocompleteHandler):
  """Return JSON to autocomplete a Site ID based on a prefix."""
  model_class = ndb_models.NewSite
  program_filter = True


class CaptainAutocomplete(AutocompleteHandler):
  """Return JSON to autocomplete a Captain."""
  model_class = ndb_models.Captain
  program_filter = False


class SiteAttachments(StaffOrCaptainHandler):

  def get(self, id):
    site = ndb.Key(ndb_models.NewSite, int(id)).get()
    if not site:
      webapp2.abort(404)

    attachment_model = site.attachments and site.attachments.get()  # type: ndb_models.SiteAttachments
    if not attachment_model:
      attachment_model = ndb_models.SiteAttachments()
      attachment_model.put()
      site.attachments = attachment_model.key
      site.put()

    d = {
      'site': site,
      'attachments': attachment_model.get_attachments(id)
    }
    return common.Respond(self.request, 'site_list_attachments', d)


class SiteView(StaffHandler):

  searchable_model_class = ndb_models.NewSite

  def get(self, id):
    d = dict(
      map_width=common.MAP_WIDTH, map_height=common.MAP_HEIGHT
    )
    site = ndb.Key(ndb_models.NewSite, int(id)).get()
    if not site:
      webapp2.abort(404)
    d['site_list_detail'] = True
    d['start_new_order_submit'] = common.START_NEW_ORDER_SUBMIT
    d['entries'] = [site]
    order_sheets = ndb_models.OrderSheet.query().order(ndb_models.OrderSheet.name)
    d['order_sheets'] = order_sheets

    # for document uploads
    upload_url = blobstore.create_upload_url('/room/upload_statement_of_work_attachment?site_id={}'.format(id))
    d['upload_url'] = str(upload_url)

    # document data for documents that are already attached
    attachment = None
    d['attachment'] = attachment
    return common.Respond(self.request, 'site_list_one', d)


class SiteLookup(StaffHandler):
  def get(self, site_number=None):
    if site_number is not None:
      site_number = site_number.upper()
      query = ndb_models.NewSite.query(ndb_models.NewSite.number == site_number)
      results = list(query)
      if not results:
        logging.warn("Requested site with number {0} not found".format(site_number))
        self.response.set_status(404)
        self.response.write("Could not find site # {0}".format(site_number))
        return
      if len(results) > 1:
        logging.error("Found more than one site with number {0}".format(site_number))
        self.response.set_status(500)
        self.response.write("Data corruption issue, more than one site with number {0}".format(site_number))
        return
      site = results[0]
      user = common.RoomsUser.from_request(self.request)
      if user.program_selected != site.program:
        user.staff.program_selected = site.program
        user.staff.put()
      return self.redirect_to('SiteView', id=site.key.integer_id())


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
    """had unresolved imports so replacing with quick 403"""
    return webapp2.abort(403)


class SitesAndCaptains(StaffHandler):
  """Show all Sites and their associated captains in a big list"""

  def get(self):
    user = common.RoomsUser.from_request(self.request)
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
    user = common.RoomsUser.from_request(self.request)
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
    user = common.RoomsUser.from_request(self.request)
    if self.request.POST['submit'] == EXPORT_CSV:
      self.response.content_type = 'text/csv'
      self.response.headers['Content-Disposition'] = (
        'attachment; filename=%s_site_budget.csv' % user.email)
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

  searchable_model_class = ndb_models.Staff

  model_class = ndb_models.Staff
  list_view = 'StaffList'
  template_value = 'staff'
  template_file = 'simple_form'


class CaptainList(StaffHandler):
  def get(self):
    return _EntryList(self.request, ndb_models.Captain, 'captain_list')


class Captain(EditView):

  searchable_model_class = ndb_models.Captain

  model_class = ndb_models.Captain
  list_view = 'CaptainList'
  template_value = 'captain'
  template_file = 'simple_form'


class SupplierList(StaffHandler):
  def get(self):
    return _EntryList(self.request, ndb_models.Supplier, 'supplier_list')


class Supplier(EditView):
  searchable_model_class = ndb_models.Supplier
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
  searchable_model_class = ndb_models.OrderSheet
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


class SiteExpenseList(StaffOrCaptainHandler):
  model_class = None  # 'StaffTime'
  expense_type = None  # 'Staff Time'
  table_template = None  # 'stafftime_table.html'

  def get(self, site_id=None):
    mdl_cls = getattr(ndb_models, self.model_class)
    query = mdl_cls.query()
    query = query.filter(mdl_cls.state != 'Deleted')
    query = query.filter(mdl_cls.state != 'new')
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
      user = common.RoomsUser.from_request(self.request)
      if user.program_selected:
        query = query.filter(mdl_cls.program == user.program_selected)
    return _EntryList(self.request, mdl_cls, 'site_expense_list',
                      params=params, query=query)


class SiteExpenseEditor(StaffOrCaptainHandler):
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
  searchable_model_class = ndb_models.StaffTime
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
  searchable_model_class = ndb_models.CheckRequest
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
  searchable_model_class = ndb_models.VendorReceipt
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
  searchable_model_class = ndb_models.InKindDonation
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
  searchable_model_class = ndb_models.Order
  def get(self, id):
    order = ndb.Key(ndb_models.Order, int(id)).get()
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


class OrderFlow(StaffOrCaptainHandler):
  def get(self, site_id, id=None):
    site = ndb.Key(ndb_models.NewSite, int(site_id)).get()
    if not site:
      webapp2.abort(404)
    d = dict(site=site)
    if id:
      order = ndb.Key(ndb_models.Order, int(id)).get()
      if not order:
        webapp2.abort(404)
      d['order'] = order
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
    user = common.RoomsUser.from_request(self.request)
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
    if next_key:
      k = ndb.Key(urlsafe=next_key)
      if k.kind() == 'NewSite':
        return self.redirect_to('OrderBySite', site_id=k.id())
      elif k.kind() == 'OrderSheet':
        return self.redirect_to('OrderBySheet', order_sheet_id=k.id())
      else:
        logging.warn('no plan for continuing to list of orders for kind: {}'.format(k.kind()))

    # fallback
    return self.redirect_to('OrderBySheet')  # TODO: should go somewhere better.


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


class OrderReconcile(StaffHandler):
  def get(self, order_sheet_id):
    """Reconcile filled orders."""
    user = common.RoomsUser.from_request(self.request)
    query = ndb_models.Order.query(
        ndb_models.Order.state.IN(['Being Filled', 'Reconciled']))
    order_sheet = ndb.Key(ndb_models.OrderSheet, int(order_sheet_id)).get()
    if order_sheet is not None:
      query = query.filter(ndb_models.Order.order_sheet == order_sheet.key)
    if user.program_selected is not None:
      query = query.filter(ndb_models.Order.program == user.program_selected)
    orders = list(query)
    suppliers = list(ndb_models.Supplier.query())
    d = {'orders': orders,
         'order_sheet': order_sheet,
         'suppliers': suppliers,
    }
    return common.Respond(self.request, 'order_reconcile', d)


class OrderInvoice(StaffHandler):
  def get(self, order_id):
    """Print an internal invoice for an order."""
    order = ndb.Key(ndb_models.Order, int(order_id)).get()
    if not order:
      return webapp2.abort(400)
    q = ndb_models.OrderItem.query(ndb_models.OrderItem.order == order.key)
    order_items = [oi for oi in q if oi.FloatQuantity()]
    _SortOrderItemsWithSections(order_items)
    order.SetInvoiceNumber()
    d = {'order': order,
         'order_items': order_items,
         'site': order.site.get(),
         }
    return common.Respond(self.request, 'order_invoice', d)


def _ChangeOrder(request, order_id, input_sanitizer, output_filter=None):
  """Changes an order field based on POST data from jeditable."""
  if not request.POST:
    return webapp2.abort(400)
  order = ndb.Key(ndb_models.Order, int(order_id)).get()
  if not order:
    return webapp2.abort(400)
  field = request.POST['id']
  value = input_sanitizer(request.POST['value'])
  logging.info("  setattr(order, %s, %r)", field, value)
  setattr(order, field, value)
  order.put()
  if output_filter is not None:
    value = output_filter(value)
  return request.response.out.write(value)


class ActualTotal(StaffHandler):
  def post(self, order_id):
    """Updates an order's actual_total field."""
    return _ChangeOrder(self.request, order_id, input_sanitizer=lambda v: float(v))


class ReconciliationNotes(StaffHandler):
  def post(self, order_id):
    """Updates an order's reconciliation_notes field."""
    return _ChangeOrder(self.request, order_id, input_sanitizer=lambda v: v)


class InvoiceDate(StaffHandler):
  def post(self, order_id):
    """Updates an order's invoice_date field.  value like 03/20/2012"""
    def _ParseDatePickerFormat(v):
      return datetime.datetime.strptime(v, '%m/%d/%Y')

    def _FormatDate(dt):
      """Formats a datetime as Django template filter |date:"m/d/Y" """
      return dt.strftime("%m/%d/%Y")

    return _ChangeOrder(self.request, order_id,
                        input_sanitizer=_ParseDatePickerFormat,
                        output_filter=_FormatDate)


class State(StaffHandler):
  def post(self, order_id):
    """Updates an order's state field."""
    return _ChangeOrder(self.request, order_id, input_sanitizer=lambda v: v)


class Vendor(StaffHandler):
  def post(self, order_id):
    """Updates an order's state field."""
    def _GetSupplier(supplier_id):
      return ndb.Key(ndb_models.Supplier, int(supplier_id))

    return _ChangeOrder(self.request, order_id, input_sanitizer=_GetSupplier,
                        output_filter=lambda(k):k.get().name)


model_type_string_to_handler_map = {}
for clazz in general_utils.get_all_subclasses(StaffHandler):
  if clazz.searchable_model_class:
    name = clazz.searchable_model_class.__name__
    if name in model_type_string_to_handler_map:
      logging.error("Model {} is defined as searchable model class on more than one handler".format(name))
      continue
    model_type_string_to_handler_map[clazz.searchable_model_class.__name__] = clazz


class Search(StaffHandler):

  @staticmethod  # exposed for testing
  def search_models(search_string, model_type_string=None, max_results=10):
    searchable_models = ndb_models.get_all_searchable_models()
    results = []
    for model_class in searchable_models:
      if model_class.__name__ not in model_type_string_to_handler_map:
        continue
      if model_type_string is not None and model_class.__name__ != model_type_string:
        continue
      index = search.Index(model_class.__name__)
      query = search.Query(
        query_string=search_string,
        options=search.QueryOptions(limit=max_results)
      )
      results.extend(index.search(query).results)
    results.sort(key=lambda d: d.rank, reverse=True)
    return results

  def get(self, max_results=10):
    search_string = self.request.get('search_string')
    go_to_site = self.request.get('go_to_site')
    model_type_string = None
    if not search_string and not go_to_site:
      return common.Respond(self.request, 'search', {})
    if go_to_site and search_string:
      return common.Respond(self.request, 'search', {'exc': ['cannot submit both search and go to site']})
    if go_to_site:
      max_results = 1
      model_type_string = 'NewSite'
      search_string = "number={}".format(go_to_site)
    results, exc = None, None
    try:
      results = Search.search_models(
        search_string=search_string,
        model_type_string=model_type_string,
        max_results=max_results)
    except:
      logging.exception("Failed search:")
      exc = traceback.format_exc().splitlines(False)[-3:]
    serialized_results = []
    if results:
      denominator = None
      for search_document in results:
        if not search_document or not search_document['headline']:
          continue
        denominator = denominator or float(search_document.rank)
        obj = collections.namedtuple(
          typename='DocumentNamespace',
          field_names='headline details model_type model_id'
        )
        obj.headline = search_document['headline'][0].value
        obj.details = [d.value for d in search_document['details']]
        obj.model_type = search_document['model_name'][0].value
        obj.model_id = search_document['model_key_id'][0].value
        obj.uri = webapp2.uri_for('LoadModel', model_type=obj.model_type, model_id=obj.model_id)
        obj.score = "{}%".format(round(100 * search_document.rank / denominator))
        serialized_results.append(obj)
        if go_to_site:
          handler = model_type_string_to_handler_map.get(obj.model_type)
          if handler is None:
            self.response.set_status(500)
            self.response.write(
              "model {} does not have a default handler defined in {}".format(obj.model_type, __file__))
            return
          return self.redirect_to(handler.__name__, id=obj.model_id)
    d = {'search_string': search_string, 'exception': exc, 'results': serialized_results}
    return common.Respond(self.request, 'search', d)


class LoadModel(StaffHandler):
  def get(self, model_type, model_id):
    handler = model_type_string_to_handler_map.get(model_type)
    if handler is None:
      self.response.set_status(500)
      self.response.write("model {} does not have a default handler defined in {}".format(model_type, __file__))
      return
    return self.redirect_to(handler.__name__, id=model_id)


############################################################################################
# Following is based on https://cloud.google.com/appengine/docs/standard/python/blobstore/ #
############################################################################################

class UploadSiteAttachment(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
      site_id = self.request.get('site_id')
      if site_id is None:
        msg = "{} did not receive a site_id, nothing to link to".format(self.__class__.__name__)
        send_message_with_status(self.response, msg)
        return

      attachment_type = self.request.get('attachment_type')
      if attachment_type is None:
        msg = "{} did not receive an attachment type".format(self.__class__.__name__)
        send_message_with_status(self.response, msg)
        return

      redirect_uri = webapp2.uri_for(SiteAttachments.__name__, id=site_id)
      upload_files = self.get_uploads('file')
      if not upload_files:
        logging.warning("No files to upload")
        return self.redirect(redirect_uri)

      upload = upload_files[0]
      site = ndb.Key(ndb_models.NewSite, int(site_id)).get()  # type: ndb_models.NewSite
      site.add_attachment(attachment_type, upload)
      return self.redirect(redirect_uri)


class DownloadSiteAttachment(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self):
        blob_key = str(urllib.unquote(self.request.get('blob_key')))
        if not blobstore.get(blob_key):
            self.error(404)
        else:
            self.send_blob(blobstore.BlobInfo.get(blob_key), save_as=True)

class RemoveSiteAttachment(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self):
    site_id = self.request.get('site_id')
    attachments_id = self.request.get('attachments_id')
    name = self.request.get('name')

    if site_id is None:
      send_message_with_status(self.response, "{} did not receive a site_id".format(self.__class__.__name__))
      return

    if attachments_id is None:
      send_message_with_status(self.response, "{} did not receive a attachments_id".format(self.__class__.__name__))
      return

    if name is None:
      send_message_with_status(self.response, "{} did not receive an attachment type".format(self.__class__.__name__))
      return

    attachments = ndb.Key(ndb_models.SiteAttachments, int(attachments_id)).get()  # type: ndb_models.SiteAttachments
    attachments.set_attachment_by_property_name(name, None)
    self.redirect(webapp2.uri_for(SiteAttachments.__name__, id=site_id))

############################################################################################
# The above is based on https://cloud.google.com/appengine/docs/standard/python/blobstore/ #
############################################################################################

class StaffPositionList(StaffHandler):
  def get(self):
    return _EntryList(self.request, ndb_models.StaffPosition, 'staffposition_list')


class StaffPosition(EditView):

  searchable_model_class = ndb_models.StaffPosition

  model_class = ndb_models.StaffPosition
  list_view = 'StaffPositionList'
  template_value = 'staff position'
  template_file = 'simple_form'
