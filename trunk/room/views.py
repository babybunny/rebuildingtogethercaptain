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
import forms
import models
import response
import common


PICTURE_HEIGHT, PICTURE_WIDTH = 600, 400
THUMBNAIL_HEIGHT, THUMBNAIL_WIDTH = 50, 50
MAP_WIDTH = 300
MAP_HEIGHT = 200
TEST_SITE_NUMBER = '11999ZZZ'
START_NEW_ORDER_SUBMIT = 'Start New Order'


def _EntryList(request, model_cls, template, params=None):
  """Generic method to perform a list view.

  Template should iterate over a list called 'entries'.
  Sorts entries on their 'name' attribute (which they must have).

  Args:
    request: the request object
    model_cls: the class of model, like models.Captain
    template: name of template file, like 'captain_list'
    """
  user, captain, staff = common.GetUser(request)
  entries = list(model_cls.all())
  entries.sort(key=lambda x: x.name)
  d = {'entries': entries, 'user': user }
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


def FindHome(user, default='/'):
  """Return path of user's home page, or a default page."""
  if user and user.email():
    staff = models.Staff.all().filter('email = ', user.email()).get()
    if staff:
      return urlresolvers.reverse(StaffHome)
    
    captain = models.Captain.all().filter('email = ', user.email()).get()
    if captain:
      return urlresolvers.reverse(CaptainHome)

  logging.info('Can not find Captain or Staff for user: %s' % user)

  return default


def GoHome(request):
  user = users.GetCurrentUser()
  return http.HttpResponseRedirect(FindHome(user))


def Help(request):
  return common.Respond(request, 'help')  


def Scoreboard(request):
  welcomes = models.Captain.all().order('-last_welcome').fetch(10)
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
  total_ordered = sum(o.GrandTotal() for o in models.Order.all())
  d = {'last_welcomes': welcomes,
       'num_captains': num_captains,
       'num_captains_active': num_captains_active,
       'num_captains_with_tshirt': num_captains_with_tshirt,
       'num_sites': num_sites,
       'num_sites_with_orders': num_sites_with_orders,
       'total_site_budget': total_site_budget,
       'num_orders': num_orders,
       'total_ordered': total_ordered,
       }
  return common.Respond(request, 'scoreboard', d)


def StaffHome(request):
  order_sheets = list(models.OrderSheet.all())
  order_sheets.sort(key=lambda x: x.name)
  d = {'order_sheets': order_sheets,
       'test_site_number': TEST_SITE_NUMBER,
       }
  return common.Respond(request, 'staff_home', d)


def CaptainHome(request):
  user, captain, staff = common.GetUser(request)
  if user is None:
    return http.HttpResponseRedirect('/')
  order_sheets = models.OrderSheet.all().order('name')
  sites = []
  for sitecaptain in captain.sitecaptain_set:
    site = sitecaptain.site
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

  return http.HttpResponseRedirect('/room/staff_home')

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


def SiteJump(request):
  user, _, _ = common.GetUser(request)
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

def SiteEdit(request, site_id=None):
  """Create or edit a canned order."""
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
        return http.HttpResponseRedirect(urlresolvers.reverse(SiteList, 
                                                              args=[site_id]))
    else:
      return common.Respond(request, 'staff_site', template_dict)

  else:
    return common.Respond(request, 'staff_site', template_dict)
  

def SiteNew(request):
  return SiteEdit(request, None)


def SitesWithoutOrder(request, order_sheet_id):
  order_sheet = models.OrderSheet.get_by_id(int(order_sheet_id))
  if order_sheet is None:
    return http.HttpResponseNotFound(
      'No order_sheet exists with that key (%r)' % order_sheet_id)
  all_sites = list(models.NewSite.all())
  orders = models.Order.all().filter('order_sheet =', order_sheet)
  order_sites = [o.site for o in orders]
  sites_without_order = [s for s in all_sites if s not in order_sites]
  sites_without_order.sort(key=lambda s: s.number)
  template_dict = {'sites': sites_without_order,
                   'num_sites_without_order': len(sites_without_order),
                   'num_sites': len(all_sites),
                   'order_sheet': order_sheet,
                   'EMAIL_SENDER': common.EMAIL_SENDER,
                   'EMAIL_SENDER_READABLE': common.EMAIL_SENDER_READABLE,
                   'EMAIL_LOG': common.EMAIL_LOG,
                   }
  return common.Respond(request, 'sites_without_order', template_dict)
    

def SitesWithoutOrderSendEmail(request, order_sheet_id):
  subject = request.POST['subject']
  body = request.POST['body']
  logging.info(request.POST)
  order_sheet = models.OrderSheet.get_by_id(int(order_sheet_id))
  if order_sheet is None:
    return http.HttpResponseNotFound(
      'No order_sheet exists with that key (%r)' % order_sheet_id)
  captains_by_site = {}
  site_captains = request.POST.getlist('site_captain')
  for sc in site_captains:
    site_id, captain_id = str(sc).split(' ')
    if site_id not in captains_by_site:
      captains_by_site[site_id] = []
    captains_by_site[site_id].append(captain_id)
  for site_id in captains_by_site:
    site = models.NewSite.get_by_id(int(site_id))
    if not site:
      logging.warn('no site found for ID %s, skipping email', site_id)
      continue
    captains = []
    for captain_id in captains_by_site[site_id]:
      captain = models.Captain.get_by_id(int(captain_id))
      if not captain:
        logging.warn('no captain found for ID %s, skipping email', captain_id)
        continue
      captains.append(captain)
    to = list(set([str(c.email) for c in captains]))
    template_dict = {
      'to': to,
      'captains': captains,
      'site': site,
      'order_sheet': order_sheet,
      'body': body,
      }
    
    logging.info('sending mail re: %s to %s', subject, to)
    common.SendMail(to, subject, body,
                    'sites_without_order_email.html', template_dict)
  return http.HttpResponseRedirect(urlresolvers.reverse(StaffHome))

def CaptainList(request):
  """Request / show all Captains.

  Was   return _EntryList(request, models.Captain, 'captain_list')
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
    return common.Respond(request, 'person', 
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


def ItemList(request):
  """Request / -- show all items."""
  return _EntryList(request, models.Item, 'item_list')

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
  
  if original_unit_cost != item.unit_cost:
    logging.info('unit_cost changed from %0.2f to %0.2f, updating orders', 
                 original_unit_cost, item.unit_cost)
    order_items = models.OrderItem.all().filter('item =', item)
    order_items.filter('quantity !=', 0)
    for order_item in order_items:
      order = order_item.order
      if order is None:
        logging.info('skipping non-existent order')
        continue
      logging.info('updating sub_total for order %d with %d items', 
                   order_item.order.key().id(), order_item.quantity)
      order_item.order.UpdateSubTotal()
      
  return http.HttpResponseRedirect(urlresolvers.reverse(ItemList))


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
      if quantity.isdigit():
        quantity = int(quantity)
      else:
        quantity = 0
      inventory_item.quantity = quantity
      inventory_item.put()


  inventory_items = list(models.InventoryItem.all())
  inventory_items.sort(key=lambda x: x.item.name)
  return common.Respond(request, 'inventory', 
                        {'invitems': inventory_items})

def CheckRequestList(request):
  """Request / -- show all CheckRequest."""
  return _EntryList(request, models.CheckRequest, 'checkrequest_list')

def CheckRequestView(request, id):
  """Printable static view of a CheckRequest."""
  check_request = models.CheckRequest.get_by_id(int(id))
  return common.Respond(request, 'checkrequest_view', 
                        {'check_request': check_request})

def CheckRequestEdit(request, id):
  """Create or edit a CheckRequest."""
  user, captain, staff = common.GetUser(request)
  check_request = None
  readable = 'Check Request'
  if id:
    check_request = models.CheckRequest.get_by_id(int(id))
    if check_request is None:
      return http.HttpResponseNotFound(
        'No %s exists with that key (%r)' % (readable, id))
    what = 'Changing existing %s' % readable
  else:
    what = 'Adding new %s' % readable
  form = forms.CheckRequestForm(data=request.POST or None,  
                                instance=check_request)
  if not request.POST:
    return common.Respond(request, 'checkrequest', 
                          {'form': form, 'check_request': check_request,
                           'what_you_are_doing': what})
  errors = form.errors
  if not errors:
    try:
      check_request = form.save(commit=False)
    except ValueError, err:
      errors['__all__'] = unicode(err)
  if errors:
    return common.Respond(request, 'checkrequest', 
                          {'form': form, 
                           'check_request': check_request})
  check_request.last_editor = user
  check_request.put()
  user = captain or staff
  if user: 
    subj = 'Check Request #%s for Site #%s Updated by %s' % (
      check_request.key().id(), 
      check_request.site.number,
      user.name)
    common.NotifyAdminViaMail(subj, 
                              template='checkrequest_email.html', 
                              template_dict={'check_request': check_request})
  return http.HttpResponseRedirect(urlresolvers.reverse(
      SiteList, args=[check_request.site.key().id()]))

def CheckRequestNew(request, site_id):
  """Create a item.  GET shows a blank form, POST processes it."""
  user, user_captain, staff = common.GetUser(request)
  site = models.NewSite.get_by_id(int(site_id))
  check_request = models.CheckRequest(site=site, captain=user_captain)
  check_request.put()
  return CheckRequestEdit(request, check_request.key().id())

