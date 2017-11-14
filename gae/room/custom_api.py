"""Non-CRU API and composite messages"""

import logging
import webapp2

from google.appengine.ext import ndb
from protorpc import message_types
from protorpc import messages
from protorpc import remote
from protorpc.wsgi import service

import base_api
import ndb_models
import protorpc_messages

package = 'rooms'


class OrderFormChoice(messages.Message):
  id = messages.IntegerField(1)
  name = messages.StringField(2)
  code = messages.StringField(3)
  visibility = messages.StringField(4)


class OrderFormChoices(messages.Message):
  order_form = messages.MessageField(OrderFormChoice, 1, repeated=True)


class OrderFormDetail(messages.Message):
  order_sheet = messages.MessageField(protorpc_messages.OrderSheet, 1)
  sorted_items = messages.MessageField(protorpc_messages.Item, 2, repeated=True)


class OrderFull(messages.Message):
  order = messages.MessageField(protorpc_messages.Order, 1, required=True)
  order_items = messages.MessageField(protorpc_messages.OrderItem, 2, repeated=True)
  delivery = messages.MessageField(protorpc_messages.Delivery, 3)
  pickup = messages.MessageField(protorpc_messages.Pickup, 4)
  retrieval = messages.MessageField(protorpc_messages.Retrieval, 5)
  id = messages.IntegerField(6)


class SiteCaptainDetail(messages.Message):
  sitecaptain = messages.MessageField(protorpc_messages.SiteCaptain, 1)
  name = messages.StringField(2)


class SiteCaptains(messages.Message):
  sitecaptain_detail = messages.MessageField(SiteCaptainDetail, 1, repeated=True)


class CustomApi(base_api.BaseApi):
  """Protorpc service implementing a custom API for ROOM.

  This covers multi-model updates and more complex reads.
  """

  @remote.method(message_types.VoidMessage,
                 message_types.VoidMessage)
  def ehlo(self, request):
    logging.info('ehlo')
    return message_types.VoidMessage()

  @remote.method(message_types.VoidMessage,
                 OrderFormChoices)
  def order_form_choices(self, request):
    res = OrderFormChoices()
    for m in ndb_models.OrderSheet.query():
      f = OrderFormChoice(
        id=m.key.integer_id(), name=m.name,
        code=m.code, visibility=m.visibility)
      res.order_form.append(f)
    return res

  @remote.method(protorpc_messages.SimpleId, OrderFormDetail)
  def order_form_detail(self, request):
    res = OrderFormDetail()
    if not request.id:
      raise remote.ApplicationError('id is required')
    key = ndb.Key(ndb_models.OrderSheet, request.id)
    mdl = key.get()
    if not mdl:
      raise remote.ApplicationError(
        'No OrderSheet found with key {}'.format(request.id))
    res.order_sheet = protorpc_messages.OrderSheetModelToMessage(mdl)
    ims = list(ndb_models.Item.query(ndb_models.Item.appears_on_order_form == key))
    ndb_models._SortItemsWithSections(ims)
    for im in ims:
      i = protorpc_messages.ItemModelToMessage(im)
      res.sorted_items.append(i)
    return res

  @remote.method(protorpc_messages.SimpleId, OrderFull)
  def order_full_read(self, request):
    self._authorize_staff()
    res = OrderFull()
    order_key = ndb.Key(ndb_models.Order, request.id)
    order_mdl = order_key.get()
    if order_mdl is None:
      raise remote.ApplicationError(
        'No Order found with key {}'.format(request.id))
    res.id = order_key.integer_id()
    res.order = protorpc_messages.OrderModelToMessage(order_mdl)

    for oi_mdl in ndb_models.OrderItem.query(ndb_models.OrderItem.order == order_key):
      res.order_items.append(protorpc_messages.OrderItemModelToMessage(oi_mdl))

    join_mdl = ndb_models.OrderDelivery.query(ndb_models.OrderDelivery.order == order_key).get()
    if join_mdl is not None:
      res.delivery = protorpc_messages.DeliveryModelToMessage(join_mdl.delivery.get())

    join_mdl = ndb_models.OrderPickup.query(ndb_models.OrderPickup.order == order_key).get()
    if join_mdl is not None:
      res.pickup = protorpc_messages.PickupModelToMessage(join_mdl.pickup.get())

    join_mdl = ndb_models.OrderRetrieval.query(ndb_models.OrderRetrieval.order == order_key).get()
    if join_mdl is not None:
      res.retrieval = protorpc_messages.RetrievalModelToMessage(join_mdl.retrieval.get())

    return res

  def _order_full_put(self, request, order=None):
    # TODO ndb.start_transaction ...
    if order is None:
      order = ndb_models.Order()
    order = protorpc_messages.OrderMessageToModel(request.order, order)
    sub_total = 0.
    for oimsg in request.order_items:
      if oimsg.quantity:
        item = ndb.Key(ndb_models.Item, oimsg.item).get()  # TODO: get_multi
        if item.unit_cost:
          sub_total += oimsg.quantity * item.unit_cost
    order.sub_total = sub_total
    if not order.state:
      order.state = 'Received'
    order.put()

    if request.delivery:
      if request.delivery.id:
        delivery = ndb.Key(ndb_models.Delivery, request.delivery.id).get()
        if not delivery:
          logging.error('no Delivery found with id {}'.format(request.delivery.id))
          webapp2.abort(404)
      else:
        delivery = ndb_models.Delivery(site=order.site)
        
      protorpc_messages.DeliveryMessageToModel(request.delivery, delivery)
      delivery.put()
      if not request.delivery.id:
        ndb_models.OrderDelivery(order=order.key, delivery=delivery.key).put()
      
    if request.pickup:
      if request.pickup.id:
        pickup = ndb.Key(ndb_models.Pickup, request.pickup.id).get()
        if not pickup:
          logging.error('no Pickup found with id {}'.format(request.pickup.id))
          webapp2.abort(404)
      else:
        pickup = ndb_models.Pickup(site=order.site)
        
      protorpc_messages.PickupMessageToModel(request.pickup, pickup)
      pickup.put()
      if not request.pickup.id:
        ndb_models.OrderPickup(order=order.key, pickup=pickup.key).put()
      
    if request.retrieval:
      if request.retrieval.id:
        retrieval = ndb.Key(ndb_models.Retrieval, request.retrieval.id).get()
        if not retrieval:
          logging.error('no Retrieval found with id {}'.format(request.retrieval.id))
          webapp2.abort(404)
      else:
        retrieval = ndb_models.Retrieval(site=order.site)
        
      protorpc_messages.RetrievalMessageToModel(request.retrieval, retrieval)
      retrieval.put()
      if not request.retrieval.id:
        ndb_models.OrderRetrieval(order=order.key, retrieval=retrieval.key).put()
      
    for oimsg in request.order_items:
      oimsg.order = order.key.integer_id()
      protorpc_messages.OrderItemMessageToModel(
        oimsg, ndb_models.OrderItem()).put()  # TODO: put_multi

  @remote.method(OrderFull, message_types.VoidMessage)
  def order_full_create(self, request):
    self._authorize_staff()
    if request.id:
      raise remote.ApplicationError('must not have id in create')
    self._order_full_put(request)
    return message_types.VoidMessage()

  @remote.method(OrderFull, message_types.VoidMessage)
  def order_full_update(self, request):
    self._authorize_staff()
    if not request.id:
      raise remote.ApplicationError('id is required')
    mdl = ndb.Key(ndb_models.Order, request.id).get()
    if not mdl:
      raise remote.ApplicationError(
        'No Order found with key {}'.format(request.id))
    self._order_full_put(request, mdl)
    return message_types.VoidMessage()

  @remote.method(protorpc_messages.SimpleId, SiteCaptains)
  def sitecaptains_for_site(self, request):
    res = SiteCaptains()
    sitecaptain_models = list(
      ndb_models.SiteCaptain.query(ndb_models.SiteCaptain.site == ndb.Key(ndb_models.NewSite, request.id)))
    for m in sitecaptain_models:
      f = protorpc_messages.SiteCaptainModelToMessage(m)
      captain_model = ndb.Key(ndb_models.Captain, f.captain).get()  # TODO: get_multi
      detail = SiteCaptainDetail(sitecaptain=f, name=captain_model.name)
      res.sitecaptain_detail.append(detail)
    return res


application = service.service_mapping(CustomApi, r'/custom_api')
