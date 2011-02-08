"""Views and methods related to handling orders."""

import csv
import logging

from django.core import urlresolvers 
from django import http
from google.appengine.ext import db

import common
import models
import views

ORDER_EXPORT_CHECKBOX_PREFIX='order_export_'
SALES_TAX_RATE = 0.0925


def OrderList(request, order_sheet_id=None, state=None):
  """Request / -- show all orders."""
  user, _, _ = common.GetUser(request)
  d = _OrderListInternal(order_sheet_id, state)
  return common.Respond(request, 'order_list', d)

def _OrderListInternal(order_sheet_id, state):
  q = models.Order.all().filter('state != ', 'new')
  order_sheet = None
  if order_sheet_id:
    order_sheet = models.OrderSheet.get_by_id(int(order_sheet_id))
    if order_sheet is not None:
      q.filter('order_sheet = ', order_sheet)
  orders = list(q)
  return {'orders': orders,
          'order_sheet': order_sheet,
          'order_export_checkbox_prefix': 
          ORDER_EXPORT_CHECKBOX_PREFIX,
          }


def OrderView(request, order_id):
  order = models.Order.get_by_id(int(order_id))
  q = models.OrderItem.all().filter('order = ', order).filter('quantity != ', 0)
  order_items = list(q)
  _SortOrderItemsWithSections(order_items)
  d = {'order': order,
       'order_items': order_items,
       'action_verb': 'Review',
       }
  return common.Respond(request, 'order_fulfill', d)
  
def OrderFulfill(request, order_id, order_sheet_id=None):
  """Start the fulfillment process for an order."""
  d = _OrderFulfillInternal(order_id, order_sheet_id)
  return common.Respond(request, 'order_fulfill', d)

def _OrderFulfillInternal(order_id, order_sheet_id):
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
  return {'order': order,
          'order_sheet': order_sheet,
          'order_items': order_items,
          'back_to_list_url': list_url,
          'confirm_url': confirm_url,
          'action_verb': 'Fulfill',
          }

def OrderFulfillConfirm(request, order_id, order_sheet_id=None):
  return _OrderFulfillConfirmInternal(order_id, order_sheet_id)

def _OrderFulfillConfirmInternal(order_id, order_sheet_id):
  order = models.Order.get_by_id(int(order_id))
  order.state = 'Being Filled'
  order.put()
  args = []
  if order_sheet_id is None:
    return http.HttpResponseRedirect(urlresolvers.reverse(OrderList))
  else:
    next_id = int(order_sheet_id)
    next_object = models.OrderSheet.get_by_id(next_id)
    if next_object is not None:
      return http.HttpResponseRedirect(urlresolvers.reverse(
          OrderList, args=[next_id]))
      
    next_object = models.NewSite.get_by_id(next_id)
    if next_object is not None:
      return http.HttpResponseRedirect(urlresolvers.reverse(
              views.SiteList, args=[next_id]))
  

def OrderExport(request):
  """Export orders as CSV."""
  user, _, _ = common.GetUser(request)
  response = http.HttpResponse(mimetype='text/csv')
  response['Content-Disposition'] = (
    'attachment; filename=%s_orders.csv' % user.email())
  _OrderExportInternal(response, request.POST)
  return response

def _OrderExportInternal(writable, post_vars):
  """Write orders as CSV to a file-like object."""   
  orders = []
  for var in post_vars:
    if var.startswith(ORDER_EXPORT_CHECKBOX_PREFIX):
      order_id = int(var[len(ORDER_EXPORT_CHECKBOX_PREFIX):])
      orders.append(models.Order.get_by_id(order_id))
  writer = csv.writer(writable)
  for o in orders:
    writer.writerow(['Order ID',
                     'site.number',
                     'order_sheet.name',
                     'sub_total',
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


def _SortOrderItemsWithSections(order_items):
  order_items.sort(
    key=lambda x: (x.item.order_form_section or None, x.item.name))
  prev_section = None
  for o in order_items:
    new_section = o.item.order_form_section or None
    if prev_section != new_section:
      o.first_in_section = True
    prev_section = new_section


def _OrderPut(request, user, order):
  order_items = list(models.OrderItem.all().filter('order = ', order))
  _SortOrderItemsWithSections(order_items)  
  if order.state == 'new':
    what = 'Starting a new order.'
    submit_button_text = "Submit this order and proceed to delivery options"
  else:
    what = 'Changing an existing order.'
    submit_button_text = 'Submit changes and proceed to delivery options'
  form = models.OrderForm(
    data=request.POST or None, 
    files=request.FILES or None,
    instance=order)

  # A little sketchy, but the best way to adjust HTML attributes of a field.
  form['notes'].field.widget.attrs['cols'] = 120
  form['notes'].field.widget.attrs['rows'] = max(
    5, len(form.instance.VisibleNotes().splitlines()))
  created_by_user = common.GetUser(request, 
                                   order.modified_by)[0],
  template_dict = {'form': form, 
                   'notes_field': form['notes'],
                   'order': order, 
                   'order_items': order_items,
                   'created_by_user': common.GetUser(request, 
                                                     order.created_by)[0],
                   'modified_by_user': common.GetUser(request, 
                                                      order.modified_by)[0],
                   'sales_tax_pct': SALES_TAX_RATE * 100.,
                   'what_you_are_doing': what,
                   'submit_button_text': submit_button_text,
                   }

  if not request.POST or request.POST['submit'] == views.START_NEW_ORDER_SUBMIT:
    return None, template_dict

  errors = form.errors
  if not errors:
    try:
      order = form.save(commit=False)
    except ValueError, err:
      errors['__all__'] = unicode(err)
  if errors:
    template_dict['errors'] = errors
    return None, template_dict

  # List of pairs: OrderItem key, new quantity
  for arg in request.POST:
    if arg.startswith('item_'):
      _, order_item_key = arg.split('_', 1)
      quantity = request.POST[arg]
      if quantity.isdigit():
        quantity = int(quantity)
      else:
        quantity = 0
      order_item = models.OrderItem.get(order_item_key)
      if quantity != order_item.quantity:
        order_item.quantity = quantity
        order_item.put()

  order.UpdateSubTotal()

  order.last_editor = user
  order.state = 'Received'
  order.put()

  return http.HttpResponseRedirect('/room/order/logistics/%s/' 
                                   % order.key().id()), None


def OrderLogistics(request, order_id):
  logging.info('OrderLogistics(%s) POST(%s)', order_id, request.POST)
  order = models.Order.get_by_id(int(order_id))
  if order is None:
    logging.warning('order is none')
    return http.HttpResponseRedirect(urlresolvers.reverse(views.CaptainHome))
  
  od = None
  ods = list(order.orderdelivery_set)
  if ods:
    od = ods[0]
    delivery = od.delivery
  else:
    delivery = models.Delivery(site=order.site)

  form = models.DeliveryForm(
    data=request.POST or None, 
    files=request.FILES or None,
    instance=delivery)

  template_dict = {'form': form,
                   'delivery': delivery,
                   'order': order}

  if not request.POST:
    return common.Respond(request, 'order_logistics', template_dict)
    
  errors = form.errors
  if not errors:
    try:
      delivery = form.save(commit=False)
    except ValueError, err:
      errors['__all__'] = unicode(err)
  if errors:
    template_dict['errors'] = errors
    return common.Respond(request, 'order_logistics', template_dict)
  
  
  delivery.put()
  if od is None:
    models.OrderDelivery(delivery=delivery, order=order).put()
  return http.HttpResponseRedirect('/room/site/list/%s/' 
                                   % order.site.key().id())


def OrderEdit(request, order_id):
  """Create or edit a order.  GET shows a blank form, POST processes it."""
  user, _, _ = common.GetUser(request)
  if user is None:
    return http.HttpResponseRedirect(users.CreateLoginURL(request.path))
  redirect, template_dict =  _OrderEditInternal(request, user, order_id)
  if redirect is not None:
      return redirect
  else:
      return common.Respond(request, 'order', template_dict)

def _OrderEditInternal(request, user, order_id):
  logging.info('OrderEdit(%s) POST(%s)', order_id, request.POST)
  order = models.Order.get_by_id(int(order_id))
  if order is None:
    logging.warning('order is none')
    return http.HttpResponseRedirect(urlresolvers.reverse(views.CaptainHome)), None
  return _OrderPut(request, user, order)


def OrderNew(request, site_id=None, order_sheet_code=None):
  """Create a new order and forward to the edit screen."""
  user, _, _ = common.GetUser(request)
  if user is None:
    return http.HttpResponseRedirect(users.CreateLoginURL(request.path))
  site = models.NewSite.get_by_id(int(site_id))
  order_sheet = models.OrderSheet.all().filter(
    'code = ', order_sheet_code).get()
  # TODO: error if order_sheet is None
  order = models.Order(site=site, order_sheet=order_sheet, state='new')
  order.put()

  items = db.GqlQuery('SELECT * FROM Item WHERE appears_on_order_form = :1',
                      order.order_sheet)
  for item in items:
    order_item = models.OrderItem(order=order, item=item)
    order_item.put()
  redirect, template_dict = _OrderPut(request, user, order)
  if redirect is not None:
      return redirect
  else:
      return common.Respond(request, 'order', template_dict)
