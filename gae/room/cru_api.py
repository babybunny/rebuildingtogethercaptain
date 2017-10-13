import six
from google.appengine.ext import ndb
from protorpc import remote
from protorpc.wsgi import service

import base_api
import models_v2
import protorpc_messages

package = 'rooms'


basic_crud_config = (
  (protorpc_messages.Jurisdiction,
   models_v2.Jurisdiction,
   protorpc_messages.JurisdictionMessageToModel,
   protorpc_messages.JurisdictionModelToMessage),
  (protorpc_messages.Staff,
   models_v2.Staff,
   protorpc_messages.StaffMessageToModel,
   protorpc_messages.StaffModelToMessage),
  (protorpc_messages.Captain,
   models_v2.Captain,
   protorpc_messages.CaptainMessageToModel,
   protorpc_messages.CaptainModelToMessage),
  (protorpc_messages.Supplier,
   models_v2.Supplier,
   protorpc_messages.SupplierMessageToModel,
   protorpc_messages.SupplierModelToMessage),
  (protorpc_messages.Site,
   models_v2.Site,
   protorpc_messages.SiteMessageToModel,
   protorpc_messages.SiteModelToMessage),
  (protorpc_messages.Site,
   models_v2.Site,  # TODO: remove
   protorpc_messages.SiteMessageToModel,
   protorpc_messages.SiteModelToMessage),
  (protorpc_messages.OrderSheet,
   models_v2.OrderSheet,
   protorpc_messages.OrderSheetMessageToModel,
   protorpc_messages.OrderSheetModelToMessage),
  (protorpc_messages.StaffTime,
   models_v2.StaffTime,
   protorpc_messages.StaffTimeMessageToModel,
   protorpc_messages.StaffTimeModelToMessage),
  (protorpc_messages.CheckRequest,
   models_v2.CheckRequest,
   protorpc_messages.CheckRequestMessageToModel,
   protorpc_messages.CheckRequestModelToMessage),
  (protorpc_messages.VendorReceipt,
   models_v2.VendorReceipt,
   protorpc_messages.VendorReceiptMessageToModel,
   protorpc_messages.VendorReceiptModelToMessage),
  (protorpc_messages.InKindDonation,
   models_v2.InKindDonation,
   protorpc_messages.InKindDonationMessageToModel,
   protorpc_messages.InKindDonationModelToMessage),
  (protorpc_messages.Item,
   models_v2.Item,
   protorpc_messages.ItemMessageToModel,
   protorpc_messages.ItemModelToMessage),
  (protorpc_messages.Order,
   models_v2.Order,
   protorpc_messages.OrderMessageToModel,
   protorpc_messages.OrderModelToMessage),
  (protorpc_messages.SiteCaptain,
   models_v2.SiteCaptain,
   protorpc_messages.SiteCaptainMessageToModel,
   protorpc_messages.SiteCaptainModelToMessage),

  # (protorpc_messages.Example,
  #  ndb_models.Example,
  #  protorpc_messages.ExampleMessageToModel,
  #  protorpc_messages.ExampleModelToMessage),
)


class _GeneratedCruApi(remote._ServiceClass):  # sorry. but 'remote' used metaclass so we have to as well.
  """Metaclass for adding CRU methods to a service, based on a config."""

  def __new__(mcs, name, bases, dct):
    """Set up mcs dict so it will have methods wrapped by remote.method.

    This is necessary to get the protorpc service to notice the methods, since
    it does so in remote._Service metaclass.
    """

    def makeBasicCrud(msg_name, msg_cls, mdl_cls, g2d, d2g):
      """Create functions for three basic CRU operations on a model.

      CRU == Create, Read, Update.  

      We don't have generic Delete methods for all models because many
      have references or back-references. These need special handling
      to avoid dangling references. Deletes should be implemented in
      custom methods.

      Args:
        msg_name: name of the Message
        msg_cls: class of the message, defined above
        mdl_cls: class of the ndb model
        g2d: function to copy a message into a model.  g2d(msg, mdl)
        d2g: function to copy a model into a new message.  msg = d2g(mdl)

      Returns:
        three CRU functions, each usable as a Protorpc remote method
      """

      def mdl_read(self, request):
        self._authorize_staff()
        if not request.id:
          raise remote.ApplicationError('id is required')
        mdl = ndb.Key(mdl_cls, request.id).get()
        if not mdl:
          raise remote.ApplicationError(
            'No {} found with key {}'.format(msg_name, request.id))
        return d2g(mdl)

      def mdl_create(self, request):
        self._authorize_staff()
        if request.id:
          raise remote.ApplicationError(
            'Must not include id with create requests')
        mdl = mdl_cls()
        g2d(request, mdl)
        mdl.put()
        return d2g(mdl)

      def mdl_update(self, request):
        self._authorize_staff()
        if not request.id:
          raise remote.ApplicationError('id is required')
        mdl = ndb.Key(mdl_cls, request.id).get()
        if not mdl:
          raise remote.ApplicationError(
            'No {} found with key {}'.format(msg_name, request.id))
        g2d(request, mdl)
        mdl.put()
        return d2g(mdl)

      return mdl_create, mdl_read, mdl_update

    # Create the CRU methods for each model and stick them in the class dict,
    # where the protorpc service will find them.
    # See remote._ServiceClass.__new__ and look for __remote_methods.
    for msg, mdl, g2d, d2g in basic_crud_config:
      msg_name = msg.__name__
      mdl_create, mdl_read, mdl_update = makeBasicCrud(msg_name, msg, mdl, g2d, d2g)

      msg_x2_wrapper = remote.method(msg, msg)
      id_msg_wrapper = remote.method(protorpc_messages.SimpleId, msg)

      func_name = '{}_create'.format(msg_name.lower())
      mdl_create.__name__ = func_name
      dct[func_name] = msg_x2_wrapper(mdl_create)

      func_name = '{}_read'.format(msg_name.lower())
      mdl_read.__name__ = func_name
      dct[func_name] = id_msg_wrapper(mdl_read)

      func_name = '{}_update'.format(msg_name.lower())
      mdl_update.__name__ = func_name
      dct[func_name] = msg_x2_wrapper(mdl_update)

    return type.__new__(mcs, name, bases, dct)


class RoomApi(six.with_metaclass(_GeneratedCruApi, base_api.BaseApi)):
  """Protorpc service implementing a CRUD API for ROOM models"""
  pass


application = service.service_mapping(RoomApi, r'/cru_api')
