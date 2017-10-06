import six
from google.appengine.ext import ndb
from protorpc import remote
from protorpc.wsgi import service

import common
import ndb_models
from protorpc_messages import *

package = 'rooms'


basic_crud_config = (
  (Jurisdiction, ndb_models.Jurisdiction,
   JurisdictionMessageToModel, JurisdictionModelToMessage),
  (Staff, ndb_models.Staff,
   StaffMessageToModel, StaffModelToMessage),
  (Captain, ndb_models.Captain,
   CaptainMessageToModel, CaptainModelToMessage),
  (Supplier, ndb_models.Supplier,
   SupplierMessageToModel, SupplierModelToMessage),
  (NewSite, ndb_models.NewSite,
   NewSiteMessageToModel, NewSiteModelToMessage),
  (Site, ndb_models.NewSite,  # TODO: remove
   SiteMessageToModel, SiteModelToMessage),
  (OrderSheet, ndb_models.OrderSheet,
   OrderSheetMessageToModel, OrderSheetModelToMessage),
  (StaffTime, ndb_models.StaffTime,
   StaffTimeMessageToModel, StaffTimeModelToMessage),
  (CheckRequest, ndb_models.CheckRequest,
   CheckRequestMessageToModel, CheckRequestModelToMessage),
  (VendorReceipt, ndb_models.VendorReceipt,
   VendorReceiptMessageToModel, VendorReceiptModelToMessage),
  (InKindDonation, ndb_models.InKindDonation,
   InKindDonationMessageToModel, InKindDonationModelToMessage),
  (Item, ndb_models.Item,
   ItemMessageToModel, ItemModelToMessage),
  (Order, ndb_models.Order,
   OrderMessageToModel, OrderModelToMessage),
  (SiteCaptain, ndb_models.SiteCaptain,
   SiteCaptainMessageToModel, SiteCaptainModelToMessage),

  #  (Example, ndb_models.Example,
  # ExampleMessageToModel, ExampleModelToMessage),
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
      id_msg_wrapper = remote.method(SimpleId, msg)

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


class RoomApi(six.with_metaclass(_GeneratedCruApi, remote.Service)):
  """Protorpc service implementing a CRUD API for ROOM models"""

  # Stash the request state so we can get at the HTTP headers later.
  def initialize_request_state(self, request_state):
    self.rs = request_state

  def _authorize_staff(self):
    """Simply call this to ensure that the user has a Staff record.

    Raises:
      remote.ApplicationError if the user is not Staff.
    """
    user, status = common.GetUser(self.rs)
    if user and user.staff:
      return
    raise remote.ApplicationError('Must be staff to use this API.')

  def _authorize_user(self):
    """Simply call this to ensure that the user has a ROOMS record.

    Raises:
      remote.ApplicationError if the user is not Staff or Captain.
    """
    user, status = common.GetUser(self.rs)
    if user and (user.staff or user.captain):
      return
    raise remote.ApplicationError('Must be a ROOMS user to use this API.')


application = service.service_mapping(RoomApi, r'/wsgi_service')
