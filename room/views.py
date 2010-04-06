# Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Views for staff functionailty."""

# TODO: combine Captain stuff with the generic Person stuff that handles 
# the Staff and Supplier views.

import csv
import datetime
import logging
import os
from google.appengine.api import images
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.db import djangoforms
from google.appengine.ext.webapp import template

import django
from django import http
from django import shortcuts
from django.core import urlresolvers 
import models
import response


PICTURE_HEIGHT, PICTURE_WIDTH = 600, 400
THUMBNAIL_HEIGHT, THUMBNAIL_WIDTH = 50, 50
MAP_WIDTH = 300
MAP_HEIGHT = 200
SALES_TAX_RATE = 0.0925
START_NEW_ORDER_SUBMIT = 'Start New Order'
HELP_CONTACT = 'al@rebuildingtogetherpeninsula.org'
TEST_SITE_NUMBER = '10100ZZZ'


def _GetUser(request, user=None):
  if user is None:
    user = users.GetCurrentUser()
  captain = models.Captain.all().filter('email = ', user.email()).get()
  user.captain = captain
  staff = models.Staff.all().filter('email = ', user.email()).get()  
  user.staff = staff
  return user, captain, staff


def _EntryList(request, model_cls, template, params=None):
  """Generic method to perform a list view.

  Template should iterate over a list called 'entries'.
  Sorts entries on their 'name' attribute (which they must have).

  Args:
    request: the request object
    model_cls: the class of model, like models.Captain
    template: name of template file, like 'captain_list'
    """
  user, captain, staff = _GetUser(request)
  entries = list(model_cls.all())
  entries.sort(key=lambda x: x.name)
  d = {'entries': entries, 'user': user }
  if params:
    d.update(params)
  return _Respond(request, template, d)


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


def _Respond(request, template_name, params=None):
  """Helper to render a response, passing standard stuff to the response.

  Args:
    request: The request object.
    template_name: The template name; '.html' is appended automatically.
    params: A dict giving the template parameters; modified in-place.

  Returns:
    Whatever render_to_response(template_name, params) returns.

  Raises:
    Whatever render_to_response(template_name, params) raises.
  """
  user, _, _ = _GetUser(request)
  if params is None:
    params = {}
  if user:
    params['user'] = user
    params['sign_out'] = users.CreateLogoutURL('/')
    params['is_admin'] = (users.IsCurrentUserAdmin() and
                          'Dev' in os.getenv('SERVER_SOFTWARE'))
  else:
    params['sign_in'] = users.CreateLoginURL(request.path)
  params['help_contact'] = HELP_CONTACT
  if not template_name.endswith('.html'):
    template_name += '.html'
  return shortcuts.render_to_response(template_name, params)


def Welcome(request):
  params = {}
  user, _, _  = _GetUser(request)
  params['user'] = user
  if user.captain:
    params['last_welcome'] = user.captain.last_welcome
    user.captain.last_welcome = datetime.datetime.now()
    user.captain.put()
    params['captain'] = user.captain
  if user.staff:
    params['last_welcome'] = user.staff.last_welcome
    user.staff.last_welcome = datetime.datetime.now()
    user.staff.put()
    params['staff'] = user.staff
  return _Respond(request, 'welcome', params)
    

def Help(request):
  return _Respond(request, 'help')  


def StaffHome(request):
  welcomes = models.Captain.all().order('-last_welcome').fetch(10)
  order_sheets = list(models.OrderSheet.all())
  order_sheets.sort(key=lambda x: x.name)
  num_captains = models.Captain.all().count()
  num_captains_active = models.Captain.all().filter(
    'last_welcome != ', None).count()
  num_captains_with_tshirt = models.Captain.all().filter(
    'tshirt_size != ', None).count()
  num_sites = models.NewSite.all().count()
  num_sites_with_orders = len(set(
      (o.site for o in models.Order.all().filter('state != ', 'new'))))
  total_site_budget = sum(s.budget for s in models.NewSite.all() 
                          if s.budget)
  num_orders = models.Order.all().count()
  total_ordered = sum(o.grand_total for o in models.Order.all() 
                      if o.grand_total)
  d = {'last_welcomes': welcomes,
       'order_sheets': order_sheets,
       'num_captains': num_captains,
       'num_captains_active': num_captains_active,
       'num_captains_with_tshirt': num_captains_with_tshirt,
       'num_sites': num_sites,
       'num_sites_with_orders': num_sites_with_orders,
       'total_site_budget': total_site_budget,
       'num_orders': num_orders,
       'total_ordered': total_ordered,
       'test_site_number': TEST_SITE_NUMBER,
       }
  return _Respond(request, 'staff_home', d)


def CaptainHome(request):
  user, captain, staff = _GetUser(request)
  if user is None:
    return http.HttpResponseRedirect('/')
  order_sheets = models.OrderSheet.all().order('name')
  sites = []
  for sitecaptain in captain.sitecaptain_set:
    site = sitecaptain.site
    site.new_order_form = models.NewOrderForm(initial=dict(site=site.key()))
    sites.append(site)
  AnnotateSitesWithEditability(sites, captain, staff)
  captain_form = models.CaptainContactForm(data=request.POST or None,
                                           instance=captain)
  return _Respond(request, 'captain_home', 
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
  return _Respond(request, 'order_sheet_list', {'order_sheets': order_sheets})


def OrderSheetEdit(request, order_sheet_id=None):
  """Create or edit a canned order."""
  user, _, _ = _GetUser(request)
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

  form = models.OrderSheetForm(data=request.POST or None, 
                                instance=order_sheet)
  if not request.POST:
    return _Respond(request, 'order_sheet', 
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
    return _Respond(request, 'order_sheet', 
                    {'form': form, 
                     'order_sheet': order_sheet})

  order_sheet.put()

  return http.HttpResponseRedirect('/room/staff_home')

def OrderSheetNew(request):
  """Create a item.  GET shows a blank form, POST processes it."""
  return OrderSheetEdit(request, None)


def OrderSheetItemDelete(request, code):
  """Delete Items that appear on the OrderSheet designated by code."""
  ors = models.OrderSheet.all().filter('code = ', code).get()
  ois = models.Item.all().filter('appears_on_order_form = ', ors).fetch(1000)
  deleted = 0
  for oi in ois:    
    oi.delete()
    deleted += 1
  return StaffHome(request)


def AnnotateSitesWithEditability(entries, captain, staff):
  for site in entries:
    if staff or (captain and site.sitecaptain_set 
                 and captain in [sc.captain for sc in site.sitecaptain_set]):
      site.editable_by_current_user = True
    else:
      site.editable_by_current_user = False


def SiteJump(request):
  user, _, _ = _GetUser(request)
  d = {'user': user}
  number = request.GET['number']
  site = models.NewSite.all().filter('number = ', number).get()
  if site is None:
    return http.HttpResponseRedirect(
      urlresolvers.reverse(StaffHome))
  else:
    return http.HttpResponseRedirect(
      urlresolvers.reverse(SiteList, args=[site.key().id()]))
    

def SiteListByNumber(request, site_number):
  site = models.NewSite.all().filter('number = ', site_number).get()
  return _SiteListInternal(request, site)


def SiteList(request, site_id=None, new_order_form=None):
  site = None
  if site_id is not None:
    site = models.NewSite.get_by_id(int(site_id))
  return _SiteListInternal(request, site, new_order_form)


def _SiteListInternal(request, site=None, new_order_form=None):
  """Request / -- show all canned orders."""
  params = dict(map_width=MAP_WIDTH, map_height=MAP_HEIGHT)
  user, _, _ = _GetUser(request)
  d = {'user': user}
  if site is not None:
    template = 'site_list_one'
    if new_order_form is None:
      site.new_order_form = models.NewOrderForm(initial=dict(site=site.key()))
    else:
      site.new_order_form = new_order_form
    entries = [site]
    d['site_list_detail'] = True
    d['start_new_order_submit'] = START_NEW_ORDER_SUBMIT
  else:
    template = 'site_list_all'
    entries = list(models.NewSite.all())
    entries.sort(key=lambda x: x.number)
  AnnotateSitesWithEditability(entries, user.captain, user.staff)
  d['entries'] = entries
  order_sheets = models.OrderSheet.all().order('name')
  d['order_sheets'] = order_sheets
  if params:
    d.update(params)
  return _Respond(request, template, d)

def SiteEdit(request, site_id=None):
  """Create or edit a canned order."""
  user, captain, staff = _GetUser(request)
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
    form_class = models.NewSiteForm
  elif (captain and site.sitecaptain_set 
        and captain in [sc.captain for sc in site.sitecaptain_set]):
    form_class = models.CaptainSiteForm
  else:
    template_dict = {'what_you_are_doing': 'Not permitted to edit this site.'}
    return _Respond(request, 'staff_site', template_dict)

  form = form_class(data=None, instance=site)
    
  form_submit = 'Save changes to Site Info'
  sitecaptain_form = models.SiteCaptainSiteForm()
  sitecaptain_form_submit = 'Add a Captain'
  sitecaptain_delete_form_submit = 'Delete'
  delete_sitecaptain = 'delete_sitecaptain'
  orders = None
  if site:
    orders = list(site.order_set)
    orders.sort(key=lambda x: x.order_sheet.name)

  template_dict = {'site': site, 
                   'staff': staff,
                   'captain': captain,
                   'orders': orders,
                   'form': form,
                   'form_submit': form_submit,
                   'sitecaptain_form': sitecaptain_form,
                   'sitecaptain_form_submit': sitecaptain_form_submit,
                   'delete_sitecaptain': delete_sitecaptain,
                   'what_you_are_doing': what}

  if request.POST:
    if request.POST['submit'] == form_submit:
      form = form_class(data=request.POST, instance=site)
      template_dict['form'] = form
      if _TryToSaveForm(form):
        if staff:
          return http.HttpResponseRedirect(
            urlresolvers.reverse(SiteList, args=[form.instance.key().id()]))
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
      sitecaptain_form = models.SiteCaptainSiteForm(data=request.POST or None)
      template_dict['sitecaptain_form'] = sitecaptain_form
      save_form = sitecaptain_form

      # Set the current site in the form, so it can be saved.
      if not save_form.is_valid():  # creates cleaned_data as a side effect
        return _Respond(request, 'staff_site', template_dict)
      save_form.cleaned_data['site'] = site
      
      # Avoid entering duplicate SiteCaptains.
      for sitecaptain in site.sitecaptain_set:
        if (sitecaptain.captain == save_form.cleaned_data['captain']
            and sitecaptain.type == save_form.cleaned_data['type']):
          save_form.errors['__all__'] = 'That Captain already exists.'
          return _Respond(request, 'staff_site', template_dict)

      if _TryToSaveForm(save_form):
        return http.HttpResponseRedirect(urlresolvers.reverse(SiteList, 
                                                              args=[site_id]))
    else:
      return _Respond(request, 'staff_site', template_dict)

  else:
    return _Respond(request, 'staff_site', template_dict)
  

def SiteNew(request):
  return SiteEdit(request, None)


def CaptainList(request):
  """Request / show all Captains.

  Was   return _EntryList(request, models.Captain, 'captain_list')
  but we need special handling for sitecaptains.
  """
  user, captain, staff = _GetUser(request)
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
  return _Respond(request, 'captain_list', d)


def CaptainEdit(request, captain_id=None):
  """Create or edit a Captain."""
  user, user_captain, staff = _GetUser(request)
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
    form_class = models.CaptainForm
  elif user_captain and user_captain == captain:
    form_class = models.CaptainContactForm
  else: 
    template_dict = {
      'what_you_are_doing': 'Not permitted to edit this Captain.'}
    return _Respond(request, 'captain', template_dict)

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

  return _Respond(request, 'captain', template_dict)

def CaptainNew(request):
  """Create a item.  GET shows a blank form, POST processes it."""
  return CaptainEdit(request, None)

def _PersonEdit(request, id, person_cls, form_cls, template, readable):
  user, _, _ = _GetUser(request)
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
    return _Respond(request, template, 
                    {'form': form, 'person': person,
                     'what_you_are_doing': what})
  errors = form.errors
  if not errors:
    try:
      person = form.save(commit=False)
    except ValueError, err:
      errors['__all__'] = unicode(err)
  if errors:
    return _Respond(request, 'person', 
                    {'form': form, 
                     'person': person})
  person.put()
  return http.HttpResponseRedirect('/room/')

def StaffList(request):
  """Request / -- show all Staff."""
  return _EntryList(request, models.Staff, 'staff_list')

def StaffEdit(request, staff_id=None):
  """Create or edit a Staff."""
  return _PersonEdit(request, staff_id, models.Staff, models.StaffForm,
                     'staff', 'Staff')

def StaffNew(request):
  """Create a item.  GET shows a blank form, POST processes it."""
  return StaffEdit(request, None)

def SupplierList(request):
  """Request / -- show all Suppliers."""
  return _EntryList(request, models.Supplier, 'supplier_list')

def SupplierEdit(request, supplier_id=None):
  """Create or edit a Supplier."""
  return _PersonEdit(request, supplier_id, models.Supplier, models.SupplierForm,
                     'supplier', 'Supplier')

def SupplierNew(request):
  """Create a item.  GET shows a blank form, POST processes it."""
  return SupplierEdit(request, None)


def ItemList(request):
  """Request / -- show all items."""
  return _EntryList(request, models.Item, 'item_list')

def ItemEdit(request, item_id=None):
  """Create or edit a item.  GET shows a blank form, POST processes it."""
  user, _, _ = _GetUser(request)
  if user is None:
    return http.HttpResponseRedirect(users.CreateLoginURL(request.path))

  item = None
  if item_id:
    item = models.Item.get(db.Key.from_path(models.Item.kind(), int(item_id)))
    if item is None:
      return http.HttpResponseNotFound('No item exists with that key (%r)' %
                                       item_id)
    what = 'Changing existing Item'
  else:
    what = 'Adding new Item'

  form = models.ItemForm(data=request.POST or None, files=request.FILES or None,
                         instance=item)

  if not request.POST:
    return _Respond(request, 'item', {'form': form, 'item': item, 
                                      'what_you_are_doing': what})
  
  errors = form.errors
  if not errors:
    try:
      item = form.save(commit=False)
    except ValueError, err:
      errors['__all__'] = unicode(err)
  if errors:
    return _Respond(request, 'item', {'form': form, 'item': item})

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

  return http.HttpResponseRedirect('/room/')


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


def OrderList(request, order_sheet_id=None, state=None):
  """Request / -- show all orders."""
  user, _, _ = _GetUser(request)
  q = models.Order.all().filter('state != ', 'new')
  order_sheet = None
  if order_sheet_id:
    order_sheet = models.OrderSheet.get_by_id(int(order_sheet_id))
    q.filter('order_sheet = ', order_sheet)
  orders = list(q)
  return _Respond(request, 'order_list', 
                 {'orders': orders,
                  'order_sheet': order_sheet,
                  'order_export_checkbox_prefix': ORDER_EXPORT_CHECKBOX_PREFIX,
                  })

def OrderFulfill(request, order_id, order_sheet_id=None):
  """Start the fulfillment process for an order."""
  order = models.Order.get_by_id(int(order_id))
  q = models.OrderItem.all().filter('order = ', order).filter('quantity != ', 0)
  order_items = list(q)
  _SortOrderItemsWithSections(order_items)
  order_sheet = None
  list_args = []
  confirm_args = [int(order_id)]
  if order_sheet_id:
    order_sheet = models.OrderSheet.get_by_id(int(order_sheet_id))
    list_args.append(int(order_sheet_id))
    confirm_args.append(int(order_sheet_id))
  list_url = urlresolvers.reverse(OrderList, args=list_args)
  confirm_url = urlresolvers.reverse(OrderFulfillConfirm, args=confirm_args)
  return _Respond(request, 'order_fulfill', 
                  {'order': order,
                   'order_sheet': order_sheet,
                   'order_items': order_items,
                   'back_to_list_url': list_url,
                   'confirm_url': confirm_url,
                   })

def OrderFulfillConfirm(request, order_id, order_sheet_id=None):
  order = models.Order.get_by_id(int(order_id))
  order.state = 'Being Filled'
  order.put()
  args = []
  if order_sheet_id is not None:
    args = [int(order_sheet_id)]
  return http.HttpResponseRedirect(urlresolvers.reverse(
      OrderList, args=args))


ORDER_EXPORT_CHECKBOX_PREFIX='order_export_'
def OrderExport(request):
  """Export orders as CSV."""
  user, _, _ = _GetUser(request)
  orders = []
  for var in request.POST:
    if var.startswith(ORDER_EXPORT_CHECKBOX_PREFIX):
      order_id = int(var[len(ORDER_EXPORT_CHECKBOX_PREFIX):])
      orders.append(models.Order.get_by_id(order_id))
  response = http.HttpResponse(mimetype='text/csv')
  response['Content-Disposition'] = (
    'attachment; filename=%s_orders.csv' % user.email())
  writer = csv.writer(response)
  for o in orders:
    writer.writerow(['Order ID',
                     'site.number',
                     'order_sheet.name',
                     'sub_total',
                     'sales_tax',
                     'grand_total',
                     'delivery_date',
                     'delivery_contact',
                     'delivery_contact_phone',
                     'delivery_location',
                     'pickup_on',
                     'number_of_days',
                     'return_on',
                     'notes',
                     'state',
                     'created',
                     'created_by',
                     'modified',
                     'modified_by',
                     ])
    writer.writerow([o.key().id(),
                     o.site.number,
                     o.order_sheet.name,
                     o.sub_total,
                     o.sales_tax,
                     o.grand_total,
                     o.delivery_date,
                     o.delivery_contact,
                     o.delivery_contact_phone,
                     o.delivery_location,
                     o.pickup_on,
                     o.number_of_days,
                     o.return_on,
                     o.notes,
                     o.state,
                     o.created,
                     o.created_by,
                     o.modified,
                     o.modified_by,
                     ])
    order_items = list(oi for oi in o.orderitem_set if oi.quantity)
    if order_items:
      order_items.sort(key=lambda x: (x.item.order_form_section, x.item.name))
      writer.writerow(['', 
                       'item.order_form_section',
                       'item.name', 
                       'item.unit_cost',
                       'item.measure',
                       'quantity', 
                       'supplier',
                       ])
    else:
      writer.writerow(['', 'No Items in this Order!!!'])
    for oi in order_items:
      writer.writerow(['', 
                       oi.item.order_form_section,
                       oi.item.name,
                       oi.item.unit_cost,
                       oi.item.measure,
                       oi.quantity,
                       oi.supplier,
                       ])
    writer.writerow([''])
  return response


def _SortOrderItemsWithSections(order_items):
  order_items.sort(key=lambda x: (x.item.order_form_section, x.item.name))
  prev_section = None
  for o in order_items:
    new_section = o.item.order_form_section or None
    if prev_section != new_section:
      o.first_in_section = True
    prev_section = new_section


def _OrderEditInternal(request, user, order):
  logging.info('Order %s', order)
  order_items = list(models.OrderItem.all().filter('order = ', order))
  _SortOrderItemsWithSections(order_items)
  if order.state == 'new':
    what = 'Starting a new order.'
    submit_button_text = "Submit this order"
  else:
    what = 'Changing an existing order.'
    submit_button_text = "Submit changes to this order"

  form = models.OrderForm(
    data=request.POST or None, 
    files=request.FILES or None,
    instance=order)
  # A little sketchy, but the best way to adjust HTML attributes of a field.
  form['notes'].field.widget.attrs['cols'] = 120
  form['notes'].field.widget.attrs['rows'] = max(
    5, len(form.instance.VisibleNotes().splitlines()))
  template_dict = {'form': form, 
                   'notes_field': form['notes'],
                   'delivery_fields': (form['delivery_date'],
                                       form['delivery_contact'],
                                       form['delivery_contact_phone'],
                                       form['delivery_location']),
                   'durable_fields':  (form['pickup_on'],
                                       form['number_of_days']),
                   'order': order, 
                   'order_items': order_items,
                   'created_by_user': _GetUser(request, order.created_by)[0],
                   'modified_by_user': _GetUser(request, order.modified_by)[0],
                   'sales_tax_pct': SALES_TAX_RATE * 100.,
                   'what_you_are_doing': what,
                   'submit_button_text': submit_button_text}
  
  if not request.POST or request.POST['submit'] == START_NEW_ORDER_SUBMIT:
    return _Respond(request, 'order', template_dict)

  errors = form.errors
  if not errors:
    try:
      order = form.save(commit=False)
    except ValueError, err:
      errors['__all__'] = unicode(err)
  if errors:
    template_dict['errors'] = errors
    return _Respond(request, 'order', template_dict)

  sub_total = 0.
  for arg in request.POST:
    if arg.startswith('item_'):
      _, order_item_key = arg.split('_', 1)
      order_item = models.OrderItem.get(order_item_key)
      quantity = request.POST[arg]
      if quantity.isdigit():
        quantity = int(quantity)
      else:
        quantity = 0
      order_item.quantity = quantity
      order_item.put()
      sub_total += quantity * order_item.item.unit_cost

  order.sub_total = sub_total
  sales_tax = sub_total * SALES_TAX_RATE
  order.sales_tax = sales_tax
  order.grand_total = sub_total + sales_tax
  order.last_editor = user
  order.state = 'Received'
  order.put()

  return http.HttpResponseRedirect('/room/site/list/%s/' % order.site.key().id())


def OrderEdit(request, order_id):
  """Create or edit a order.  GET shows a blank form, POST processes it."""
  user, _, _ = _GetUser(request)
  if user is None:
    return http.HttpResponseRedirect(users.CreateLoginURL(request.path))
  logging.info('OrderEdit(%s) POST(%s)', order_id, request.POST)
  order = models.Order.get_by_id(int(order_id))
  if order is None:
    logging.warning('order is none')
    return http.HttpResponseRedirect(urlresolvers.reverse(CaptainHome))
  return _OrderEditInternal(request, user, order)


def OrderNew(request, site_id=None, order_sheet_code=None):
  """Create a new order and forward to the edit screen."""
  user, _, _ = _GetUser(request)
  if user is None:
    return http.HttpResponseRedirect(users.CreateLoginURL(request.path))
  site = models.NewSite.get_by_id(int(site_id))
  order_sheet = models.OrderSheet.all().filter(
    'code = ', order_sheet_code).get()
  order = models.Order(site=site, order_sheet=order_sheet, state='new')
  order.put()

  items = db.GqlQuery('SELECT * FROM Item WHERE appears_on_order_form = :1',
                      order.order_sheet)
  for item in items:
    order_item = models.OrderItem(order=order, item=item)
    order_item.put()
  return _OrderEditInternal(request, user, order)


def Inventory(request):
  """Update the inventory.  POST saves the form, GET just displays."""
  user, _, _ = _GetUser(request)
  if user is None:
    return http.HttpResponseRedirect(users.CreateLoginURL(request.path))

  for arg in request.POST:    
    if arg.startswith('item_'):
      _, inventory_item_key = arg.split('_', 1)
      inventory_item = models.InventoryItem.get(inventory_item_key)
      quantity = request.POST[arg]
      if quantity.isdigit():
        quantity = int(quantity)
      else:
        quantity = 0
      inventory_item.quantity = quantity
      inventory_item.put()


  inventory_items = list(models.InventoryItem.all())
  inventory_items.sort(key=lambda x: x.item.name)
  return _Respond(request, 'inventory', 
                  {'invitems': inventory_items})
