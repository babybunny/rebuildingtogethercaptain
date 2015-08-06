"""Views and methods related to handling orders."""

import collections
import csv
import datetime
import logging

from django.core import urlresolvers
from django import http
from google.appengine.ext import db

import common
import forms
import models
import views

FULFILL_MULTIPLE = 'Fulfill Multiple Orders'
SALES_TAX_RATE = 0.0925


def OrderList(request, order_sheet_id=None):
  """Request / -- show all orders."""
  user, _, _ = common.GetUser(request)
  d = _OrderListInternal(order_sheet_id, user.program_selected)
  return common.Respond(request, 'order_list', d)


def _OrderListInternal(order_sheet_id, program=None):
  query = models.Order.all().filter('state != ', 'new')
  if program is not None:
    query.filter('program =', program)
  order_sheet = None
  if order_sheet_id:
    order_sheet = models.OrderSheet.get_by_id(int(order_sheet_id))
    if order_sheet is not None:
      query.filter('order_sheet = ', order_sheet)
  orders = list(query)
  mass_action = {'export_csv': views.EXPORT_CSV,
                 'fulfill_many': FULFILL_MULTIPLE}
  return {'orders': orders,
          'order_sheet': order_sheet,
          'export_checkbox_prefix':
          views.POSTED_ID_PREFIX,
          'mass_action': mass_action,
          'num_being_filled': len([o for o in orders
                                   if o.state == 'Being Filled'])
          }


def OrderReconcile(request, order_sheet_id=None):
  """Reconcile filled orders."""
  user, _, _ = common.GetUser(request)
  d = _OrderReconcileInternal(order_sheet_id, user.program_selected)
  return common.Respond(request, 'order_reconcile', d)


def _OrderReconcileInternal(order_sheet_id, program=None):
  query = models.Order.all().filter(
      'state IN ', ['Being Filled', 'Reconciled'])
  order_sheet = models.OrderSheet.get_by_id(int(order_sheet_id))
  if order_sheet is not None:
    query.filter('order_sheet = ', order_sheet)
  if program is not None:
    query.filter('program =', program)
  orders = list(query)
  suppliers = list(models.Supplier.all())

  return {'orders': orders,
          'order_sheet': order_sheet,
          'suppliers': suppliers,
          }


def ChangeOrder(request, order_id, input_sanitizer, output_filter=None):
  """Changes an order field based on POST data from jeditable."""
  user, captain, staff = common.GetUser(request)
  if not staff:
    return http.HttpResponse(status=400)
  if not request.POST:
    return http.HttpResponse(status=400)
  order = models.Order.get_by_id(int(order_id))
  if not order:
    return http.HttpResponse(status=400)
  field = request.POST['id']
  value = input_sanitizer(request.POST['value'])
  logging.info("  setattr(order, %s, %r)", field, value)
  setattr(order, field, value)
  order.put()
  if output_filter is not None:
    value = output_filter(value)
  return http.HttpResponse(value, status=200)


def ActualTotal(request, order_id):
  """Updates an order's actual_total field."""
  return ChangeOrder(request, order_id, input_sanitizer=lambda v: float(v))


def ReconciliationNotes(request, order_id):
  """Updates an order's reconciliation_notes field."""
  return ChangeOrder(request, order_id, input_sanitizer=lambda v: v)


def InvoiceDate(request, order_id):
  """Updates an order's invoice_date field.  value like 03/20/2012"""
  def _ParseDatePickerFormat(v):
    return datetime.datetime.strptime(v, '%m/%d/%Y')

  def _FormatDate(dt):
    """Formats a datetime as Django template filter |date:"m/d/Y" """
    return dt.strftime("%m/%d/%Y")

  return ChangeOrder(request, order_id,
                     input_sanitizer=_ParseDatePickerFormat,
                     output_filter=_FormatDate)


def State(request, order_id):
  """Updates an order's state field."""
  return ChangeOrder(request, order_id, input_sanitizer=lambda v: v)


def Vendor(request, order_id):
  """Updates an order's state field."""
  def _GetSupplier(supplier_id):
    return models.Supplier.get_by_id(int(supplier_id))

  return ChangeOrder(request, order_id, input_sanitizer=_GetSupplier)


def OrderView(request, order_id):
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


def OrderDeleteConfirm(request, order_sheet_id=None):
  order_ids = views.PostedIds(request.POST)
  return _OrderConfirmInternal(order_ids, order_sheet_id,
                               state='Deleted')

# TODO: combine two methods below once tests are OK.


def OrderFulfillConfirm(request, order_sheet_id=None):
  order_ids = views.PostedIds(request.POST)
  return _OrderFulfillConfirmInternal(order_ids, order_sheet_id)


def _OrderFulfillConfirmInternal(order_ids, order_sheet_id):
  return _OrderConfirmInternal(order_ids, order_sheet_id,
                               state='Being Filled')


def _OrderConfirmInternal(order_ids, order_sheet_id, state):
  orders = models.Order.get_by_id(order_ids)
  for order in orders:
    order.state = state
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
          views.SiteView, args=[next_id]))

FULFULL_OR_DELETE_OPTIONS = {
    'fulfill': {
        'action_verb': 'Fulfill',
        'confirm_method': OrderFulfillConfirm,
        'submit_value': 'Click here to print and confirm fulfillment has started',
        'should_print': True,
    },
    'delete':  {
        'action_verb': 'Delete',
        'confirm_method': OrderDeleteConfirm,
        'submit_value': 'Click here to confirm deletion',
        'should_print': False,
    },
}


def OrderDelete(request, order_id, order_sheet_id=None):
  """Prompt user to delete the order."""
  d = _OrderFulfillInternal([order_id], order_sheet_id, mode='delete')
  return common.Respond(request, 'order_fulfill', d)


def OrderFulfill(request, order_id, order_sheet_id=None):
  """Start the fulfillment process for an order."""
  d = _OrderFulfillInternal([order_id], order_sheet_id, mode='fulfill')
  return common.Respond(request, 'order_fulfill', d)


def _OrderFulfillInternal(order_ids, order_sheet_id, mode):
  options = FULFULL_OR_DELETE_OPTIONS[mode]
  orders = []
  for order_id in order_ids:
    order = models.Order.get_by_id(int(order_id))
    q = models.OrderItem.all().filter('order = ', order)
    order_items = [oi for oi in q if oi.FloatQuantity()]
    _SortOrderItemsWithSections(order_items)
    orders.append({'order': order,
                   'order_items': order_items})

  order_sheet = None
  list_args = []
  confirm_args = []
  if order_sheet_id:
    order_sheet = models.OrderSheet.get_by_id(int(order_sheet_id))
    list_args.append(int(order_sheet_id))
    confirm_args.append(int(order_sheet_id))
  list_url = urlresolvers.reverse(OrderList, args=list_args)
  confirm_url = urlresolvers.reverse(options['confirm_method'],
                                     args=confirm_args)
  orders.sort(key=lambda o: o['order'].site.number)
  return {'orders': orders,
          'order_sheet': order_sheet,
          'order_items': order_items,
          'back_to_list_url': list_url,
          'confirm_url': confirm_url,
          'action_verb': options['action_verb'],
          'submit_value': options['submit_value'],
          'should_print': options['should_print'],
          'show_logistics_details': True,
          'num_orders': len(orders),
          'export_checkbox_prefix':
          views.POSTED_ID_PREFIX,
          }


def OrderExport(request):
  """Export orders as CSV."""
  user, _, _ = common.GetUser(request)
  if request.POST['submit'] == views.EXPORT_CSV:
    response = http.HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename=%s_orders.csv' % user.email())
    _OrderExportInternal(response, request.POST)
    return response
  elif request.POST['submit'] == FULFILL_MULTIPLE:
    order_ids = views.PostedIds(request.POST)
    order_sheet_id = request.POST.get('order_sheet_id')
    d = _OrderFulfillInternal(order_ids, order_sheet_id, mode='fulfill')
    return common.Respond(request, 'order_fulfill', d)


def _OrderExportInternal(writable, post_vars):
  """Write orders as CSV to a file-like object."""
  order_ids = views.PostedIds(post_vars)
  orders = list(models.Order.get_by_id(order_ids))
  orders.sort(key=lambda o: o.site.number)
  writer = csv.writer(writable)
  writer.writerow(['Site Number',
                   'Order ID',
                   'Order modified',
                   'Street Address',
                   'City State Zip',
                   'Order Note',
                   'Type',
                   'Item',
                   'Quantity',
                   'Measure',
                   'Subtotal ($)',
                   'LogisticsStart',
                   'LogisticsEnd',
                   'LogisticsInstructions',
                   'Optional Item Note',
                   ])
  order_items_by_order = collections.defaultdict(list)
  # 30 is the magic filter limit, experimentally derived
  for i in range(0, len(orders), 30):
    batch_orders = orders[i:i + 30]
    logging.info('loading batch of %d orders starting with %d',
                 len(batch_orders), i)
    q = models.OrderItem.all()
    q.filter('order IN ', batch_orders)
    order_items = [oi for oi in q if oi.FloatQuantity()]
    order_items.sort(key=lambda x: (x.item.order_form_section, x.item.name))
    for oi in order_items:
      o = oi.order
      order_id = o.key().id()
      row = [o.site.number,
             o.key().id(),
             o.modified.date().isoformat(),
             o.site.street_number,
             o.site.city_state_zip,
             o.notes,
             oi.item.VisibleOrderFormSection(),
             oi.item.VisibleName(),
             oi.VisibleQuantity(),
             oi.item.measure,
             oi.VisibleCost(),
             o.logistics_start,
             o.logistics_end,
             o.logistics_instructions,
             oi.name,
             ]
      order_items_by_order[order_id].append(row)

    for o in batch_orders:
      if o.key().id() not in order_items_by_order:
        row = [o.site.number,
               o.key().id(),
               o.modified.date().isoformat(),
               o.site.street_number,
               o.site.city_state_zip,
               o.notes,
               '<no items>',
               '<no items>',
               '<no items>',
               '<no items>',
               '<no items>',
               o.logistics_start,
               o.logistics_end,
               o.logistics_instructions,
               '<no items>',
               ]
        order_items_by_order[o.key().id()].append(row)

  for o in orders:
    for row in order_items_by_order[o.key().id()]:
      row = [unicode(f).encode('ascii', 'ignore') for f in row]
      writer.writerow(row)


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
    what = 'Enter quantities for items.'
    submit_button_text = 'Submit this order'
  else:
    what = 'Update quantities if necessary.'
    submit_button_text = 'Submit changes'
  if order.order_sheet.HasLogistics():
    submit_button_text += ' and proceed to delivery options'

  form_cls = forms.CaptainOrderForm
  if user.staff:
    form_cls = forms.OrderForm

  form = form_cls(
      data=request.POST or None,
      files=request.FILES or None,
      instance=order)

  # A little sketchy, but the best way to adjust HTML attributes of a field.
  form['notes'].field.widget.attrs['cols'] = 120
  form['notes'].field.widget.attrs['rows'] = max(
      5, len(form.instance.VisibleNotes().splitlines()))
  created_by_user = common.GetUser(request,
                                   order.last_editor)[0],
  template_dict = {'form': form,
                   'notes_field': form['notes'],
                   'order': order,
                   'order_items': order_items,
                   'created_by_user': common.GetUser(request,
                                                     order.created_by)[0],
                   'modified_by_user': common.GetUser(request,
                                                      order.last_editor)[0],
                   'sales_tax_pct': SALES_TAX_RATE * 100.,
                   'what_you_are_doing': what,
                   'show_instructions': True,
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
    logging.error('errors (%s)', errors)
    return None, template_dict

  # List of pairs: OrderItem key, new quantity
  for arg in request.POST:
    if arg.startswith('item_'):
      _, order_item_key = arg.split('_', 1)
      quantity = request.POST[arg]
      try:
        quantity = float(quantity)
      except ValueError:
        quantity = 0.0
      order_item = models.OrderItem.get(order_item_key)
      if quantity != order_item.quantity_float:
        order_item.quantity_float = quantity
        order_item.put()

  order.UpdateSubTotal()
  order.UpdateLogistics()

  order.last_editor = user
  order.state = 'Received'
  order.put()

  if order.order_sheet.HasLogistics():
    return http.HttpResponseRedirect(
        urlresolvers.reverse(OrderLogistics, args=[str(order.key().id())])), None
  else:
    return http.HttpResponseRedirect(urlresolvers.reverse(
        views.SiteView, args=[str(order.site.key().id())])), None


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

  op = None
  ops = list(order.orderpickup_set)
  if ops:
    op = ops[0]
    pickup = op.pickup
  else:
    pickup = models.Pickup(site=order.site)

  ot = None
  ots = list(order.orderretrieval_set)
  if ots:
    ot = ots[0]
    retrieval = ot.retrieval
  else:
    retrieval = models.Retrieval(site=order.site)

  current = {'delivery': od,
             'pickup': op,
             'retrieval': ot,
             }

  form_objects = {}
  form_objects['delivery'] = forms.DeliveryForm(
      data=request.POST or None,
      files=request.FILES or None,
      instance=delivery)
  form_objects['pickup'] = forms.PickupForm(
      data=request.POST or None,
      files=request.FILES or None,
      instance=pickup)
  form_objects['retrieval'] = forms.RetrievalForm(
      data=request.POST or None,
      files=request.FILES or None,
      instance=retrieval)

  existing_dates = []
  for d in order.site.delivery_set:
    for o in d.orderdelivery_set:
      existing_dates.append(
          (d.delivery_date, 'Delivery', o.order.order_sheet.name,
           o.order.key().id()))
  for d in order.site.pickup_set:
    for o in d.orderpickup_set:
      existing_dates.append(
          (d.pickup_date, 'Pick-up', o.order.order_sheet.name,
           o.order.key().id()))
  for d in order.site.retrieval_set:
    for o in d.orderretrieval_set:
      existing_dates.append(
          (d.dropoff_date, 'Drop-off', o.order.order_sheet.name,
           o.order.key().id()))
      existing_dates.append(
          (d.retrieval_date, 'Retrieval', o.order.order_sheet.name,
           o.order.key().id()))

  existing_dates.sort()

  captains = [sc.captain for sc in order.site.sitecaptain_set]
  captains.sort(key=lambda c: c.name)
  proceed_to_fulfill = "STAFF ONLY: proceed directly to fulfill"
  complete = {}
  complete['delivery'] = 'Choose these delivery options'
  complete['pickup'] = 'Choose these pick-up options'
  complete['retrieval'] = 'Choose these drop-off/retrieval options'
  template_dict = {'forms': form_objects,
                   'order': order,
                   'captains': captains,
                   'complete': complete,
                   'existing_dates': existing_dates,
                   'current': current,
                   'proceed_to_fulfill': proceed_to_fulfill}

  if not request.POST:
    return common.Respond(request, 'order_logistics', template_dict)

  if request.POST.get('submit', '').startswith(complete['delivery']):
    errors = form_objects['delivery'].errors
    if not errors:
      try:
        delivery = form_objects['delivery'].save(commit=False)
      except ValueError, err:
        errors['__all__'] = unicode(err)
    if errors:
      template_dict['errors'] = errors
      return common.Respond(request, 'order_logistics', template_dict)

    delivery.put()
    if od is None:
      models.OrderDelivery(delivery=delivery, order=order).put()
    if op is not None:
      logging.info('deleting OrderPickup for order %s', order.key().id())
      op.delete()

  if request.POST.get('submit', '').startswith(complete['pickup']):
    errors = form_objects['pickup'].errors
    if not errors:
      try:
        pickup = form_objects['pickup'].save(commit=False)
      except ValueError, err:
        errors['__all__'] = unicode(err)
    if errors:
      template_dict['errors'] = errors
      return common.Respond(request, 'order_logistics', template_dict)

    pickup.put()
    if op is None:
      models.OrderPickup(pickup=pickup, order=order).put()
    if od is not None:
      logging.info('deleting OrderDelivery for order %s', order.key().id())
      od.delete()

  if request.POST.get('submit', '').startswith(complete['retrieval']):
    errors = form_objects['retrieval'].errors
    if not errors:
      try:
        retrieval = form_objects['retrieval'].save(commit=False)
      except ValueError, err:
        errors['__all__'] = unicode(err)
    if errors:
      template_dict['errors'] = errors
      return common.Respond(request, 'order_logistics', template_dict)

    retrieval.put()
    if ot is None:
      models.OrderRetrieval(retrieval=retrieval, order=order).put()
    # These cases should never happen.
    if od is not None:
      logging.info('deleting OrderDelivery for order %s', order.key().id())
      od.delete()
    if op is not None:
      logging.info('deleting OrderPickup for order %s', order.key().id())
      op.delete()

  order.UpdateLogistics()

  if request.POST.get('submit', '').endswith('(STAFF ONLY)'):
    return http.HttpResponseRedirect(urlresolvers.reverse(
        OrderFulfill, args=[str(order.key().id())]))

  return http.HttpResponseRedirect(urlresolvers.reverse(
      views.SiteView, args=[str(order.site.key().id())]))


def OrderEdit(request, order_id):
  """Create or edit a order.  GET shows a blank form, POST processes it."""
  user, _, _ = common.GetUser(request)
  if user is None:
    return http.HttpResponseRedirect(users.CreateLoginURL(request.path))
  redirect, template_dict = _OrderEditInternal(request, user, order_id)
  if redirect is not None:
    return redirect
  else:
    return common.Respond(request, 'order', template_dict)


def _OrderEditInternal(request, user, order_id):
  logging.info('OrderEdit(%s) POST(%s)', order_id, request.POST)
  order = models.Order.get_by_id(int(order_id))
  if order is None:
    logging.warning('no order found with id %s', order_id)
    url = urlresolvers.reverse(views.CaptainHome)
    return http.HttpResponseRedirect(url), None

  items = list(oi.item for oi in order.orderitem_set)
  for item in order.order_sheet.item_set:
    if item in items:
      continue
    order_item = models.OrderItem(order=order, item=item)
    order_item.put()

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

  for item in order.order_sheet.item_set:
    order_item = models.OrderItem(order=order, item=item)
    order_item.put()
  redirect, template_dict = _OrderPut(request, user, order)
  if redirect is not None:
    return redirect
  else:
    return common.Respond(request, 'order', template_dict)


def OrderPreview(request, site_id=None):
  user, _, _ = common.GetUser(request)
  if user is None:
    return http.HttpResponseRedirect(users.CreateLoginURL(request.path))
  site = models.NewSite.get_by_id(int(site_id))
  existing_orders = {}
  query = site.Orders.Items()
  for order in query:
    if order.order_sheet.code not in existing_orders:
      existing_orders[order.order_sheet.code] = []
    existing_orders[order.order_sheet.code].append(order)

  order_sheets = models.OrderSheet.all().order('name')
  order_sheets = [o for o in order_sheets if o.visibility != 'Staff Only']
  for os in order_sheets:
    order_items = [models.OrderItem(item=i) for i in os.item_set]
    _SortOrderItemsWithSections(order_items)
    os.sorted_items = order_items[:]
    os.num_existing_orders = 0
    if os.code in existing_orders:
      os.existing_orders = existing_orders[os.code]
      os.num_existing_orders = len(existing_orders[os.code])

  t = {'order_sheets': order_sheets,
       'site': site}
  return common.Respond(request, 'order_preview', t)


def OrderItemName(request):
  user, _, _ = common.GetUser(request)
  if user is None:
    return http.HttpResponse(status=400)
  order_item_id = int(request.POST['id'])
  order_item = models.OrderItem.get_by_id(order_item_id)
  if order_item is None:
    return http.HttpResponse(status=400)
  order_item.name = request.POST['value']
  order_item.put()
  return http.HttpResponse(order_item.name)


def OrderUpdateLogistics(request, order_id):
  models.Order.get_by_id(int(order_id)).UpdateLogistics()
  return http.HttpResponse('OK')


def RecomputeOrderItems(o):
  for oi in o.orderitem_set:
    if not oi.quantity_float and not oi.quantity:
      oi.delete()
      continue
    if oi.quantity_float:
      continue
    if oi.quantity is not None:
      oi.quantity_float = float(oi.quantity)
      oi.put()
  o.UpdateSubTotal()
