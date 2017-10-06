import logging

from google.appengine.ext import ndb
from protorpc import message_types
from protorpc import remote
from protorpc.wsgi import service

import base_api
import ndb_models
from protorpc_messages import *

package = 'rooms'


class CustomApi(base_api.BaseApi):
  """Protorpc service implementing a custom API for ROOM.

  This covers multi-model updates and more complex reads.
  """

  @remote.method(message_types.VoidMessage,
                 message_types.VoidMessage)
  def ehlo(self, request):
    logging.info('ehlo')
    return message_types.VoidMessage()

  @remote.method(SimpleId, message_types.VoidMessage)
  def sitecaptain_delete(self, request):
    self._authorize_staff()
    ndb.Key(ndb_models.SiteCaptain, request.id).delete()
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

  @remote.method(SimpleId, OrderFormDetail)
  def order_form_detail(self, request):
    res = OrderFormDetail()
    if not request.id:
      raise remote.ApplicationError('id is required')
    key = ndb.Key(ndb_models.OrderSheet, request.id)
    mdl = key.get()
    if not mdl:
      raise remote.ApplicationError(
        'No OrderSheet found with key {}'.format(request.id))
    res.order_sheet = OrderSheetModelToMessage(mdl)
    ims = list(ndb_models.Item.query(ndb_models.Item.appears_on_order_form == key))
    ndb_models._SortItemsWithSections(ims)
    for im in ims:
      i = ItemModelToMessage(im)
      res.sorted_items.append(i)
    return res

  @remote.method(SimpleId, OrderFull)
  def order_full_read(self, request):
    self._authorize_staff()
    res = OrderFull()
    order_key = ndb.Key(ndb_models.Order, request.id)
    order_mdl = order_key.get()
    if order_mdl is None:
      raise remote.ApplicationError(
        'No Order found with key {}'.format(request.id))
    res.id = order_key.integer_id()
    res.order = OrderModelToMessage(order_mdl)

    for oi_mdl in ndb_models.OrderItem.query(ndb_models.OrderItem.order == order_key):
      res.order_items.append(OrderItemModelToMessage(oi_mdl))

    join_mdl = ndb_models.OrderDelivery.query(ndb_models.OrderDelivery.order == order_key).get()
    if join_mdl is not None:
      res.delivery = DeliveryModelToMessage(join_mdl.delivery.get())

    join_mdl = ndb_models.OrderPickup.query(ndb_models.OrderPickup.order == order_key).get()
    if join_mdl is not None:
      res.pickup = PickupModelToMessage(join_mdl.pickup.get())

    join_mdl = ndb_models.OrderRetrieval.query(ndb_models.OrderRetrieval.order == order_key).get()
    if join_mdl is not None:
      res.retrieval = RetrievalModelToMessage(join_mdl.retrieval.get())

    return res

  def _order_full_put(self, request):
    # TODO ndb.start_transaction ...
    order = OrderMessageToModel(request.order, ndb_models.Order())
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
      delivery = DeliveryMessageToModel(request.delivery,
                                        ndb_models.Delivery(site=order.site))
      delivery.put()
      ndb_models.OrderDelivery(order=order.key, delivery=delivery.key).put()
    if request.pickup:
      pickup = PickupMessageToModel(request.pickup,
                                    ndb_models.Pickup(site=order.site))
      pickup.put()
      ndb_models.OrderPickup(order=order.key, pickup=pickup.key).put()
    if request.retrieval:
      retrieval = RetrievalMessageToModel(request.retrieval,
                                          ndb_models.Retrieval(site=order.site))
      retrieval.put()
      ndb_models.OrderRetrieval(order=order.key, retrieval=retrieval.key).put()

    for oimsg in request.order_items:
      oimsg.order = order.key.integer_id()
      OrderItemMessageToModel(oimsg, ndb_models.OrderItem()).put()  # TODO: put_multi

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
        'No {} found with key {}'.format(Order, request.id))
    self._order_full_put(request)
    return message_types.VoidMessage()

  @remote.method(SimpleId, SiteCaptains)
  def sitecaptains_for_site(self, request):
    res = SiteCaptains()
    sitecaptain_models = list(
      ndb_models.SiteCaptain.query(ndb_models.SiteCaptain.site == ndb.Key(ndb_models.NewSite, request.id)))
    for m in sitecaptain_models:
      f = SiteCaptainModelToMessage(m)
      captain_model = ndb.Key(ndb_models.Captain, f.captain).get()  # TODO: get_multi
      detail = SiteCaptainDetail(sitecaptain=f, name=captain_model.name)
      res.sitecaptain_detail.append(detail)
    return res


application = service.service_mapping(CustomApi, r'/custom_api')
