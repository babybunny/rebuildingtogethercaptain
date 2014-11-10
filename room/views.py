"""General views."""

# TODO: combine Captain stuff with the generic Person stuff that handles 
# the Staff and Supplier views.

import csv
import datetime
import logging
import os
try:
  import simplejson as json
except ImportError:
  import json
from google.appengine.api import images
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.db import djangoforms
from google.appengine.ext.webapp import template

import django
from django import http
from django import shortcuts
from django.core import urlresolvers 
import forms
import models
import response
import common


PICTURE_HEIGHT, PICTURE_WIDTH = 600, 400
THUMBNAIL_HEIGHT, THUMBNAIL_WIDTH = 50, 50
MAP_WIDTH = 300
MAP_HEIGHT = 200
START_NEW_ORDER_SUBMIT = 'Start New Order'
POSTED_ID_PREFIX = 'export_'
EXPORT_CSV = 'Export CSV'


def _EntryList(request, model_cls, template, params=None, query=None):
  """Generic method to perform a list view.

  Template should iterate over a list called 'entries'.
  Sorts entries on their 'name' attribute (which they must have).

  Args:
    request: the request object
    model_cls: the class of model, like models.Captain
    template: name of template file, like 'captain_list'
    params: dict of more template parameters
    query: db.Query object to use, if not model_cls.all()
    """
  user, captain, staff = common.GetUser(request)
  if query is None:
    query = model_cls.all()
  entries = list(query)
  entries.sort(key=lambda x: x.name)
  d = {'entries': entries, 'num_entries': len(entries), 'user': user, 
       'cls': model_cls,
       'model_cls_name': model_cls.__name__ }
  if params:
    d.update(params)
  return common.Respond(request, template, d)


def _TryToSaveForm(save_form):
  """Saves form, catching errors and storing them back in the form.
  
  Args:
    save_form: djangoforms.ModelForm instance to save.
  
  Returns:
    success: True iff form was saved.
  """
  errors = save_form.errors
  if not errors:
    try:
      ob = save_form.save(commit=False)
    except ValueError, err:
      errors['__all__'] = unicode(err)
  if not errors:
    ob.put()
  return not errors


def _Autocomplete(request, model_class, program_filter=False):
  prefix = str(request.GET['term']).lower()
  
  items = model_class.all()
  items.filter('search_prefixes = ', prefix)
  if program_filter:
    user, _, _ = common.GetUser(request)  
    items.filter('program =', user.program_selected)
  matches = {}
  for c in items:
    label = c.Label()
    matches[label] = c.key().id()
  response = http.HttpResponse(mimetype='application/json')  
  response.write(json.dumps(matches))
  return response


def Help(request):
  return common.Respond(request, 'help')  


def CaptainHome(request, captain_id=None):
  user, captain, staff = common.GetUser(request)
  if user is None:
    return http.HttpResponseRedirect('/')
  if captain_id is not None:
    captain = models.Captain.get_by_id(int(captain_id))
  order_sheets = models.OrderSheet.all().order('name')
  sites = []
  for sitecaptain in captain.sitecaptain_set:
    site = sitecaptain.site
    # TODO: parameterize me!
    if site.program != '2014 NRD':
      continue
    site.new_order_form = forms.NewOrderForm(initial=dict(site=site.key()))
    sites.append(site)
  AnnotateSitesWithEditability(sites, captain, staff)
  captain_form = forms.CaptainContactForm(data=request.POST or None,
                                          instance=captain)
  return common.Respond(request, 'captain_home', 
                        {'order_sheets': order_sheets,
                         'entries': sites,
                         'captain': captain,
                         'captain_form': captain_form,
                         'captain_contact_submit': 
                         'Save changes to personal info',
                         'map_width': MAP_WIDTH, 'map_height': MAP_HEIGHT,
                         'site_list_detail': True,
                         'start_new_order_submit': START_NEW_ORDER_SUBMIT,
                         })


def OrderSheetList(request):
  """Request / -- show all canned orders."""
  order_sheets = list(models.OrderSheet.all().order('name'))
  return common.Respond(request, 'order_sheet_list', 
                        {'order_sheets': order_sheets})


def OrderSheetEdit(request, order_sheet_id=None):
  """Create or edit a canned order."""
  user, _, _ = common.GetUser(request)
  order_sheet = None
  if order_sheet_id:
    order_sheet = models.OrderSheet.get(
      db.Key.from_path(models.OrderSheet.kind(), int(order_sheet_id)))
    if order_sheet is None:
      return http.HttpResponseNotFound(
        'No order_sheet exists with that key (%r)' % order_sheet_id)
    what = 'Changing existing Order Form'
  else:
    what = 'Adding new Order Form'

  form = forms.OrderSheetForm(data=request.POST or None, 
                              instance=order_sheet)
  if not request.POST:
    return common.Respond(request, 'order_sheet', 
                          {'form': form, 
                           'order_sheet': order_sheet, 
                           'what_you_are_doing': what})
  
  errors = form.errors
  if not errors:
    try:
      order_sheet = form.save(commit=False)
    except ValueError, err:
      errors['__all__'] = unicode(err)
  if errors:
    return common.Respond(request, 'order_sheet', 
                          {'form': form, 
                           'order_sheet': order_sheet})

  order_sheet.put()

  return http.HttpResponseRedirect('/room/order_sheet/list')

def OrderSheetNew(request):
  """Create a item.  GET shows a blank form, POST processes it."""
  return OrderSheetEdit(request, None)


def AnnotateSitesWithEditability(entries, captain, staff):
  for site in entries:
    if staff or (captain and site.sitecaptain_set 
                 and captain in [sc.captain for sc in site.sitecaptain_set]):
      site.editable_by_current_user = True
    else:
      site.editable_by_current_user = False


def SiteListByNumber(request, site_number):
  site = models.NewSite.all().filter('number = ', site_number).get()
  return _SiteListInternal(request, site)


def SiteView(request, site_id=None, new_order_form=None):
  site = None
  if site_id is not None:
    site = models.NewSite.get_by_id(int(site_id))
  return _SiteListInternal(request, site, new_order_form)


def _SiteListInternal(request, site=None, new_order_form=None):
  """Request / -- show all canned orders."""
  params = dict(map_width=MAP_WIDTH, map_height=MAP_HEIGHT)
  user, _, _ = common.GetUser(request)
  d = {'user': user}
  if site is not None:
    template = 'site_list_one'
    if new_order_form is None:
      site.new_order_form = forms.NewOrderForm(initial=dict(site=site.key()))
    else:
      site.new_order_form = new_order_form
    entries = [site]
    d['site_list_detail'] = True
    d['start_new_order_submit'] = START_NEW_ORDER_SUBMIT
  else:
    # TODO: can we remove this view?
    template = 'site_list_all'
    entries = list(models.NewSite.all())
    entries.sort(key=lambda x: x.number)
  AnnotateSitesWithEditability(entries, user.captain, user.staff)
  d['entries'] = entries
  order_sheets = models.OrderSheet.all().order('name')
  d['order_sheets'] = order_sheets
  if params:
    d.update(params)
  return common.Respond(request, template, d)


def SiteExpenses(request, site_id):
  site = models.NewSite.get_by_id(int(site_id))
  return common.Respond(request, 'site_expenses', {'site': site})

def SiteSummary(request, site_id):
  site = models.NewSite.get_by_id(int(site_id))
  return common.Respond(request, 'site_summary', {'site': site})

def SiteEdit(request, site_id=None):
  """Create or edit a Site."""
  user, captain, staff = common.GetUser(request)
  site = None
  if site_id:
    site = models.NewSite.get_by_id(int(site_id))
    if site is None:
      return http.HttpResponseNotFound(
        'No site exists with that key (%r)' % site_id)
    what = 'Changing existing Site'
  else:
    what = 'Adding new Site'

  if staff:
    form_class = forms.NewSiteForm
  elif (captain and site.sitecaptain_set 
        and captain in [sc.captain for sc in site.sitecaptain_set]):
    form_class = forms.CaptainSiteForm
  else:
    template_dict = {'what_you_are_doing': 'Not permitted to edit this site.'}
    return common.Respond(request, 'staff_site', template_dict)

  form = form_class(data=None, instance=site)
    
  form_submit = 'Save changes to Site Info'
  sitecaptain_form = forms.SiteCaptainSiteForm()
  sitecaptain_form_submit = 'Add a Captain'
  sitecaptain_delete_form_submit = 'Delete'
  delete_sitecaptain = 'delete_sitecaptain'
  template_dict = {'site': site, 
                   'staff': staff,
                   'captain': captain,
                   'form': form,
                   'form_submit': form_submit,
                   'sitecaptain_form': sitecaptain_form,
                   'sitecaptain_form_submit': sitecaptain_form_submit,
                   'delete_sitecaptain': delete_sitecaptain,
                   'what_you_are_doing': what}

  if request.POST:
    if request.POST['submit'] == form_submit:
      form = form_class(data=request.POST, instance=site)
      if site is None:
        existing_site = models.NewSite.all().filter('number =', form.data['number']).get()
        if existing_site:
          return common.Respond(request, 'site_exists', {'site': existing_site})
        
      template_dict['form'] = form
      if _TryToSaveForm(form):
        if staff:
          return http.HttpResponseRedirect(
            urlresolvers.reverse(SiteView, args=[form.instance.key().id()]))
        else:
          return http.HttpResponseRedirect(
            urlresolvers.reverse(CaptainHome))
    if delete_sitecaptain in request.POST:
      for id in request.POST.getlist(delete_sitecaptain):
        sc = models.SiteCaptain.get_by_id(int(id))
        if sc is not None:
          sc.delete()
      return http.HttpResponseRedirect(urlresolvers.reverse(SiteEdit, 
                                                            args=[site_id]))

    if request.POST['submit'] == sitecaptain_form_submit:
      sitecaptain_form = forms.SiteCaptainSiteForm(data=request.POST or None)
      template_dict['sitecaptain_form'] = sitecaptain_form
      save_form = sitecaptain_form

      # Set the current site in the form, so it can be saved.
      if not save_form.is_valid():  # creates cleaned_data as a side effect
        return common.Respond(request, 'staff_site', template_dict)
      save_form.cleaned_data['site'] = site
      
      # Avoid entering duplicate SiteCaptains.
      for sitecaptain in site.sitecaptain_set:
        if (sitecaptain.captain == save_form.cleaned_data['captain']
            and sitecaptain.type == save_form.cleaned_data['type']):
          save_form.errors['__all__'] = 'That Captain already exists.'
          return common.Respond(request, 'staff_site', template_dict)

      if _TryToSaveForm(save_form):
        return http.HttpResponseRedirect(urlresolvers.reverse(SiteView, 
                                                              args=[site_id]))
    else:
      return common.Respond(request, 'staff_site', template_dict)

  else:
    return common.Respond(request, 'staff_site', template_dict)
  

def SiteNew(request):
  return SiteEdit(request, None)


def SitePut(request, site_id):
  models.NewSite.get_by_id(int(site_id)).put()
  return http.HttpResponse('OK')


def SiteAutocomplete(request):
  """Return JSON to autocomplete a Site ID based on a prefix."""
  return _Autocomplete(request, models.NewSite, program_filter=True)


def SiteAnnouncement(request, site_id):
  """Updates a site's announcement fields."""
  user, captain, staff = common.GetUser(request)
  if not staff:
    return http.HttpResponse(status=400)
  if not request.POST:
    return http.HttpResponse(status=400)
  site = models.NewSite.get_by_id(int(site_id))
  if not site:
    return http.HttpResponse(status=400)
  field = request.POST['id']
  value = request.POST['value']
  setattr(site, field, value)
  site.put()
  return http.HttpResponse(value, status=200)


def SiteList(request):
  """Request / show all Sites.

  Was return _EntryList(request, models.NewSite, 'site_list')
  but we need special handling for sitecaptains.
  """
  user, captain, staff = common.GetUser(request)
  query = models.NewSite.all().order('number')
  if staff and staff.program_selected:
    query.filter('program =', staff.program_selected)
  entries = list(query)
  sitecaptains_by_site = {}
  # TODO: this is fetching too many - we only need those for the current program
  for sc in models.SiteCaptain.all():
    sitecaptains_by_site.setdefault(sc.site.key().id(), []).append(sc)
  for s in entries:
    k = s.key().id()
    if k in sitecaptains_by_site:
      s.sitecaptains = sitecaptains_by_site[k]
  d = {'entries': entries, 'num_entries': len(entries), 'user': user, 
       'sitecaptains_by_site': sitecaptains_by_site }
  return common.Respond(request, 'site_list', d)


def SiteBudget(request):
  """List all Sites with a "Budget" view."""
  user, _, staff = common.GetUser(request)
  if not staff:
    return http.HttpResponse(status=400)  
  params = {    
    'export_csv': EXPORT_CSV,
    'export_checkbox_prefix': POSTED_ID_PREFIX
    }
  query = models.NewSite.all()
  if staff and staff.program_selected:
    query.filter('program =', staff.program_selected)
    params['program'] = staff.program_selected

  # this 'q' param is just for testing
  if 'q' in request.GET:
    query.filter('search_prefixes = ', request.GET['q'].lower())
    params['search'] = request.GET['q']

  params['jurisdiction'] = request.GET.get('j')
  if params['jurisdiction']:
    query.filter('jurisdiction = ', params['jurisdiction'])

  entries = list(query)
  total = 0
  for site in entries:
    total += site.Expenses() 

  params.update({'entries': entries, 'num_entries': len(entries), 'user': user, 
                 'total_expenses': total})
  return common.Respond(request, 'site_budget', params)


def SiteBudgetExport(request):
  """Export Site budget rows as CSV."""
  user, _, _ = common.GetUser(request)
  if request.POST['submit'] == EXPORT_CSV:
    response = http.HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = (
      'attachment; filename=%s_site_budget.csv' % user.email())
    _SiteBudgetExportInternal(response, request.POST)
    return response
      
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
  sites = list(models.NewSite.get_by_id(site_ids))
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
           ]
    row = [unicode(f).encode('ascii', 'ignore') for f in row]
    writer.writerow(row)

# TODO: could be more complete
def SiteExport(request):
  """Export all Sites as CSV."""
  user, _, _ = common.GetUser(request)
  query = models.NewSite.all().order('number')
  if staff and staff.program_selected:
    query.filter('program =', staff.program_selected)
  sites = list(query)
  response = http.HttpResponse(mimetype='text/csv')
  response['Content-Disposition'] = 'attachment; filename=room_sites.csv'
  writer = csv.writer(response)
  writer.writerow(['Site number',
                   'Name',
                   'Captains', 
                   'Type',
                   ])
  for s in sites:
    sc = list(s.sitecaptain_set)
    captains = '+'.join(set(c.captain.name for c in sc))
    type = '+'.join(set(c.type for c in sc))
    writer.writerow([s.number,
                     s.name,
                     captains,
                     type
                     ])
  return response

def SiteListDebug(request):
  """Request / show all Sites in a debug mode."""
  return _EntryList(request, models.NewSite, 'site_debug', 
                    query=models.NewSite.all().order('number'))

def CaptainList(request):
  """Request / show all Captains.

  Was return _EntryList(request, models.Captain, 'captain_list')
  but we need special handling for sitecaptains.
  """
  user, captain, staff = common.GetUser(request)
  entries = list(models.Captain.all().order('name'))
  sitecaptains_by_captain = {}
  for sc in models.SiteCaptain.all():
    sitecaptains_by_captain.setdefault(sc.captain.key().id(), []).append(sc)
  for c in entries:
    k = c.key().id()
    if k in sitecaptains_by_captain:
      c.sitecaptains = sitecaptains_by_captain[k]
  d = {'entries': entries, 'user': user, 
       'sitecaptains_by_captain': sitecaptains_by_captain }
  return common.Respond(request, 'captain_list', d)


def CaptainExport(request):
  """Export all Captains as CSV."""
  user, _, _ = common.GetUser(request)
  captains = list(models.Captain.all().order('name'))
  response = http.HttpResponse(mimetype='text/csv')
  response['Content-Disposition'] = 'attachment; filename=room_captains.csv'
  writer = csv.writer(response)
  writer.writerow(['Captain ID',
                   'Name',
                   'Email',
                   'Preferred Phone',
                   'Backup Phone',
                   'Sites', 
                   'Type',
                   'T-Shirt',                     
                   'Last Welcome',
                   'Notes'])
  for c in captains:
    sc = list(c.sitecaptain_set)
    sites = '+'.join(set(s.site.number for s in sc))
    type = '+'.join(set(s.type for s in sc))
    writer.writerow([c.key().id(),
                     c.name,
                     c.email,
                     c.phone1,
                     c.phone2,
                     sites,
                     type,
                     c.tshirt_size,
                     c.last_welcome,
                     c.notes,
                     ])
  return response


def CaptainEdit(request, captain_id=None):
  """Create or edit a Captain."""
  user, user_captain, staff = common.GetUser(request)
  captain = None
  if captain_id:
    captain = models.Captain.get_by_id(int(captain_id))
    if captain is None:
      return http.HttpResponseNotFound(
        'No captain exists with that key (%r)' % captain_id)
    what = 'Changing existing Captain'
  else:
    what = 'Adding new Captain'

  if staff:
    form_class = forms.CaptainForm
  elif user_captain and user_captain == captain:
    form_class = forms.CaptainContactForm
  else: 
    template_dict = {
      'what_you_are_doing': 'Not permitted to edit this Captain.'}
    return common.Respond(request, 'captain', template_dict)

  form = form_class(data=None, instance=captain)
  template_dict = {'form': form, 'captain': captain, 
                   'what_you_are_doing': what}

  if request.POST:
    form = form_class(data=request.POST or None, instance=captain)
    template_dict['form'] = form
    if _TryToSaveForm(form):
      if staff: 
        return http.HttpResponseRedirect(urlresolvers.reverse(CaptainList))
      else:
        return http.HttpResponseRedirect(urlresolvers.reverse(CaptainHome))

  return common.Respond(request, 'captain', template_dict)

def CaptainNew(request):
  """Create a item.  GET shows a blank form, POST processes it."""
  return CaptainEdit(request, None)

def CaptainAutocomplete(request):
  """Return JSON to autocomplete a captain ID based on a prefix."""
  return _Autocomplete(request, models.Captain)

def CaptainPut(request, captain_id):
  models.Captain.get_by_id(int(captain_id)).put()
  return http.HttpResponse('OK')

def _PersonEdit(request, id, person_cls, form_cls, template, readable):
  user, _, _ = common.GetUser(request)
  person = None
  if id:
    person = person_cls.get_by_id(int(id))
    if person is None:
      return http.HttpResponseNotFound(
        'No %s exists with that key (%r)' % (readable, id))
    what = 'Changing existing %s' % readable
  else:
    what = 'Adding new %s' % readable
  form = form_cls(data=request.POST or None,  instance=person)
  if not request.POST:
    return common.Respond(request, template, 
                          {'form': form, 'person': person,
                           'what_you_are_doing': what})
  errors = form.errors
  if not errors:
    try:
      person = form.save(commit=False)
    except ValueError, err:
      errors['__all__'] = unicode(err)
  if errors:
    return common.Respond(request, template, 
                          {'form': form, 
                           'person': person})
  person.put()
  return http.HttpResponseRedirect('/room/')

def StaffList(request):
  """Request / -- show all Staff."""
  return _EntryList(request, models.Staff, 'staff_list')

def StaffEdit(request, staff_id=None):
  """Create or edit a Staff."""
  return _PersonEdit(request, staff_id, models.Staff, forms.StaffForm,
                     'staff', 'Staff')

def StaffNew(request):
  """Create a item.  GET shows a blank form, POST processes it."""
  return StaffEdit(request, None)

def SupplierList(request):
  """Request / -- show all Suppliers."""
  return _EntryList(request, models.Supplier, 'supplier_list')

def SupplierEdit(request, supplier_id=None):
  """Create or edit a Supplier."""
  return _PersonEdit(request, supplier_id, models.Supplier, forms.SupplierForm,
                     'supplier', 'Supplier')

def SupplierNew(request):
  """Create a item.  GET shows a blank form, POST processes it."""
  return SupplierEdit(request, None)

def SupplierNewSimple(request):
  form = forms.SupplierFormSimple(data=request.POST)
  errors = form.errors
  if not errors:
    try:
      supplier = form.save(commit=False)
    except ValueError, err:
      errors['__all__'] = unicode(err)
  if errors:
    return http.HttpResponse(json.dumps({'errors': errors}))
  supplier.put()
  return http.HttpResponse(json.dumps({'key': str(supplier.key()),
                                       'name': supplier.name}))

def ItemList(request):
  """Request / -- show all items."""
  return _EntryList(request, models.Item, 'item_list')

def OrderSheetItemList(request, id):
  """Request / -- show all items in an Order Sheet."""
  sheet = models.OrderSheet.get_by_id(int(id))
  return _EntryList(request, models.Item, 'order_sheet_item_list', 
                    query=sheet.item_set, params={'order_sheet': sheet})

def ItemEdit(request, item_id=None):
  """Create or edit a item.  GET shows a blank form, POST processes it."""
  user, _, _ = common.GetUser(request)
  if user is None:
    return http.HttpResponseRedirect(users.CreateLoginURL(request.path))

  item = None
  original_unit_cost = None
  if item_id:
    item = models.Item.get(db.Key.from_path(models.Item.kind(), int(item_id)))
    if item is None:
      return http.HttpResponseNotFound('No item exists with that key (%r)' %
                                       item_id)
    what = 'Changing existing Item'
    original_unit_cost = item.unit_cost
  else:
    what = 'Adding new Item'

  form = forms.ItemForm(data=request.POST or None, files=request.FILES or None,
                        instance=item)

  if not request.POST:
    return common.Respond(request, 'item', 
                          {'form': form, 'item': item, 
                           'what_you_are_doing': what})
  
  errors = form.errors
  if not errors:
    try:
      item = form.save(commit=False)
    except ValueError, err:
      errors['__all__'] = unicode(err)
  if errors:
    return common.Respond(request, 'item', 
                          {'form': form, 'item': item})

  item.last_editor = user
  if item.picture:
    try:
      item.picture =  db.Blob(
        images.resize(item.picture, PICTURE_HEIGHT, PICTURE_WIDTH))
      item.thumbnail = db.Blob(
        images.resize(item.picture, THUMBNAIL_HEIGHT, THUMBNAIL_WIDTH))
    except images.BadImageError:
      item.picture = None
      item.thumbnail = None
  item.put()
  if not item_id:
    invitem = models.InventoryItem(item=item)
    invitem.put()

  _UpdateItemCost(original_unit_cost, item)

  return http.HttpResponseRedirect(urlresolvers.reverse(ItemList))


def ItemPrice(request, item_id):
  """Updates a Item's price field."""
  return _SetField(models.Item, float, request, item_id)


def SiteScopeOfWork(request, site_id):
  """Updates a Site's scope_of_work field."""
  return _SetField(models.NewSite, None, request, site_id)


# TODO: use for SiteAnnouncement()
def _SetField(model_cls, cast, request, id):
  user, captain, staff = common.GetUser(request)
  if not staff:
    return http.HttpResponse(status=400)
  if not request.POST:
    return http.HttpResponse(status=400)
  obj = model_cls.get_by_id(int(id))
  if not obj:
    return http.HttpResponse(status=400)
  field = request.POST['id']
  if not field:
    return http.HttpResponse(status=400)
  value = request.POST['value']
  if cast is not None:
    value = cast(value)
  setattr(obj, field, value)
  obj.put()
  return http.HttpResponse(value, status=200)


def _UpdateItemCost(original_unit_cost, item):
  """Updates subtotals for all orders containing the item."""
  if original_unit_cost == item.unit_cost:
    return
  logging.info('unit_cost changed from %0.2f to %0.2f, updating orders', 
               original_unit_cost, item.unit_cost)
  q = models.OrderItem.all().filter('item =', item)
  order_items = [oi for oi in q if oi.FloatQuantity()]
  for order_item in order_items:
    order = order_item.order
    if order is None:
      logging.info('skipping non-existent order')
      continue
    order_item.order.UpdateSubTotal()
      

def ItemNew(request):
  """Create a item.  GET shows a blank form, POST processes it."""
  return ItemEdit(request, None)

def ItemPicture(request, item_id, is_thumbnail=False):
  """Return the picture of an Item."""
  item = models.Item.get(db.Key.from_path(models.Item.kind(), int(item_id)))
  if item is None:
    return http.HttpResponseNotFound('No item exists with that key (%r)' %
                                     item_id)
  if is_thumbnail and item.thumbnail:
    image = item.thumbnail
  else:
    image = item.picture
  if not image:
    return http.HttpResponse(content='', status=404)

  size = len(image)
  if size >= 6 and image.startswith("GIF"):
    content_type = 'image/gif'
  elif size >= 8 and image.startswith("\x89PNG\x0D\x0A\x1A\x0A"):
    content_type = 'image/png'
  elif size >= 2 and image.startswith("\xff\xD8"):
    content_type = 'image/jpeg'
  elif (size >= 8 and (image.startswith("II\x2a\x00") or
                       image.startswith("MM\x00\x2a"))):
    content_type = 'image/tiff'
  elif size >= 2 and image.startswith("BM"):
    content_type = 'image/bmp'
  elif size >= 4 and image.startswith("\x00\x00\x01\x00"):
    content_type = 'image/ico'
  else: 
    content_type = 'text/plain'  # Fail!
  return http.HttpResponse(content=image, content_type=content_type)


def ItemThumbnail(request, item_id):
  return ItemPicture(request, item_id, is_thumbnail=True)


def Inventory(request):
  """Update the inventory.  POST saves the form, GET just displays."""
  user, _, _ = common.GetUser(request)
  if user is None:
    return http.HttpResponseRedirect(users.CreateLoginURL(request.path))

  for arg in request.POST:    
    if arg.startswith('item_'):
      _, inventory_item_key = arg.split('_', 1)
      inventory_item = models.InventoryItem.get(inventory_item_key)
      quantity = request.POST[arg]
      try:
        quantity = float(quantity)
      except ValueError:
        quantity = 0.0
      inventory_item.quantity_float = quantity
      inventory_item.put()


  inventory_items = list(models.InventoryItem.all())
  inventory_items.sort(key=lambda x: x.item.name)
  return common.Respond(request, 'inventory', 
                        {'invitems': inventory_items})

class SiteExpense:
  """Generic class for check requests and vendor receipts."""
  model = None  # class object of target model
  template_base = ''  # prefix of templates
  readable = ''  # Readable name of entity
  form_cls = None

  @classmethod
  def List(cls, request, site_id=None):
    """Show all."""
    query = cls.model.all().filter('state !=', 'new')
    params = {'which_site': 'All',
              'expense_type': cls.readable,
              'table_template': cls.template_base + '_table.html'}
    if site_id is not None:
      site = models.NewSite.get_by_id(int(site_id))
      query.filter('site = ', site)
      params['which_site'] = 'Site ' + site.number
    else:
      user, _, _ = common.GetUser(request)  
      query.filter('program =', user.program_selected)
    return _EntryList(request, cls.model, 'site_expense_list',
                      params=params, query=query)
  
  @classmethod
  def View(cls, request, id):
    """Printable static view of an expense."""
    entity = cls.model.get_by_id(int(id))
    return common.Respond(request, cls.template_base + '_view', 
                          {'entity': entity})

  
  @classmethod
  def New(cls, request, site_id):
    """Create an entity.  GET shows a blank form, POST processes it."""
    user, user_captain, staff = common.GetUser(request)
    site = models.NewSite.get_by_id(int(site_id))
    if user_captain:
      instance = cls.model(site=site, captain=user_captain)
    else:
      instance = cls.model(site=site)
    instance.put()
    return cls.Edit(request, instance.key().id())
  
  @classmethod
  def Edit(cls, request, id):
    """Create or edit an entity."""
    id = int(id)
    entity = cls.model.get_by_id(id)
    if entity is None:
      return http.HttpResponseNotFound(
        'No %s exists with that key (%r)' % (cls.readable, id))
    edit_id = entity.key().id()

    if entity.state == 'new':      
      what = 'Adding new %s' % cls.readable
    else:
      what = 'Changing existing %s' % cls.readable

    user, captain, staff = common.GetUser(request)
    form = cls.form_cls(data=request.POST or None,  
                        instance=entity, staff=staff)
    if cls == VendorReceipt:
      supplier_form = forms.SupplierFormSimple()
    else:
      supplier_form = None
    if not request.POST:
      return common.Respond(
        request, cls.template_base, 
        {'form': form, 
         'supplier_form': supplier_form,
         'entity': entity,
         'edit_id': edit_id,
         'what_you_are_doing': what})

    errors = form.errors
    if not errors:
      try:
        entity = form.save(commit=False)
      except ValueError, err:
        errors['__all__'] = unicode(err)
    if errors:
      return common.Respond(
        request, cls.template_base, 
        {'form': form, 
         'supplier_form': supplier_form,
         'entity': entity,
         'edit_id': edit_id,
         'what': 'Fix errors below and try submitting again.'})

    entity.last_editor = user
    if entity.state == 'new':
      entity.state = 'submitted'
    entity.put()
    user = captain or staff
    if user: 
      subj = '%s #%s for Site #%s Updated by %s' % (
        cls.readable,
        entity.key().id(), 
        entity.site.number,
        user.name)
      common.NotifyAdminViaMail(subj, 
                                template=cls.template_base + '_email.html', 
                                template_dict={'entity': entity})
    return http.HttpResponseRedirect(urlresolvers.reverse(
        SiteView, args=[entity.site.key().id()]))


class CheckRequest(SiteExpense):
  model = models.CheckRequest
  template_base = 'checkrequest'
  readable = 'Check Request'
  form_cls = forms.CheckRequestForm


# If the urlpattern cappable name has a dot in it then Django tries to 
# load the prefix as a module name.  This is a workaround.
CheckRequestNew = CheckRequest.New
CheckRequestEdit = CheckRequest.Edit
CheckRequestList = CheckRequest.List
CheckRequestView = CheckRequest.View


class VendorReceipt(SiteExpense):
  model = models.VendorReceipt
  template_base = 'vendorreceipt'
  readable = 'Vendor Receipt'
  form_cls = forms.VendorReceiptForm


VendorReceiptNew = VendorReceipt.New
VendorReceiptEdit = VendorReceipt.Edit
VendorReceiptList = VendorReceipt.List
VendorReceiptView = VendorReceipt.View


class InKindDonation(SiteExpense):
  model = models.InKindDonation
  template_base = 'inkinddonation'
  readable = 'In-kind Donation'
  form_cls = forms.InKindDonationForm


InKindDonationNew = InKindDonation.New
InKindDonationEdit = InKindDonation.Edit
InKindDonationList = InKindDonation.List
InKindDonationView = InKindDonation.View


SITE_EXPENSE_TYPES = dict((c.__name__, c) for c in (
    models.CheckRequest,
    models.VendorReceipt,
    models.InKindDonation,
    ))

def SiteExpenseState(request, item_cls, item_id):
  """Updates a site expense's state field."""
  user, captain, staff = common.GetUser(request)
  if not staff:
    return http.HttpResponse(status=400)
  if not request.POST:
    return http.HttpResponse(status=400)
  cls = SITE_EXPENSE_TYPES[item_cls]
  modl = cls.get_by_id(int(item_id))
  if not modl:
    return http.HttpResponse(status=400)
  value = request.POST['value']
  modl.state = value
  modl.put()
  return http.HttpResponse(value, status=200)

def ExpenseNew(request, site_id):
  """Creates a new Expense."""
  site = models.NewSite.get_by_id(int(site_id))
  params = {}
  if site is None:
    params['error'] = 'Site ID %s not found!' % site_id
  else:
    expense = models.Expense(site=site)
    params.update({'expense': expense})
  return common.Respond(request, 'expense.html', params)

def Expense(request, expense_id):
  """Displays or saves an Expense."""
  if request.META['REQUEST_METHOD'] == 'GET':
    expense = models.Expense.get_by_id(int(expense_id))
    params = {}
    if expense is None:
      params['error'] = 'Expense ID %s not found!' % expense_id
    else:
      params.update(
        {'expense': expense})
    return common.Respond(request, 'expense.html', params)
  elif request.META['REQUEST_METHOD'] == 'POST':
    logging.info(request.POST)

def StandardKit(request):
  return common.Respond(request, 'standard_kit.html', {})


