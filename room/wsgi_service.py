import logging
import os
import six

from protorpc import messages
from protorpc import message_types
from protorpc import remote
from protorpc.wsgi import service

from google.appengine.api import users
from google.appengine.ext import ndb

import common
import ndb_models


package = 'rooms'

class GenericResponse(messages.Message):
  message = messages.StringField(1)
  
class SimpleId(messages.Message):
  id = messages.IntegerField(1, required=True)

class Choice(messages.Message):
  id = messages.IntegerField(1, required=True)
  label = messages.StringField(2)

class Choices(messages.Message):
  choice = messages.MessageField(Choice, 1, repeated=True)

class StaffPosition(messages.Message):
  key = messages.IntegerField(1)
  position_name = messages.StringField(2)
  hourly_rate = messages.FloatField(3)
  
class Program(messages.Message):
  year = messages.IntegerField(1)
  name = messages.StringField(2)
  site_number_prefix = messages.StringField(3)
  status = messages.StringField(4)

class Programs(messages.Message):
  program = messages.MessageField(Program, 1, repeated=True)

################
# Jurisdiction #
################

def _JurisdictionModelToMessage(mdl):
  s = Jurisdiction(
    name=mdl.name,
    id=mdl.key.integer_id(),
  )
  return s

def _JurisdictionMessageToModel(msg, mdl):
  mdl.name = msg.name
  return mdl

class Jurisdiction(messages.Message):
  id = messages.IntegerField(1)
  name = messages.StringField(2)

#########
# Staff #
#########

def _StaffModelToMessage(mdl):
  s = Staff(
    name=mdl.name,
    email=mdl.email,
    last_welcome=mdl.last_welcome,
    program_selected=mdl.program_selected,
    notes=mdl.notes,
    id=mdl.key.integer_id(),
  )
  if mdl.since:
    s.since = mdl.since.isoformat()  # datetime, for display only
  return s

def _StaffMessageToModel(msg, mdl):
  mdl.name = msg.name
  mdl.email = msg.email
  mdl.last_welcome = msg.last_welcome
  mdl.program_selected = msg.program_selected
  mdl.notes = msg.notes
  # can't set "since", it's automatic
  return mdl

class Staff(messages.Message):
  id = messages.IntegerField(1)
  name = messages.StringField(2)
  email = messages.StringField(3)
  last_welcome = messages.StringField(4)
  program_selected = messages.StringField(5)
  notes = messages.StringField(6)
  since = messages.StringField(7)

###########
# Captain #
###########

def _CaptainModelToMessage(mdl):
  s = Captain(
    name=mdl.name,
    email=mdl.email,
    rooms_id=mdl.rooms_id,
    phone_mobile=mdl.phone_mobile,
    phone_work=mdl.phone_work,
    phone_home=mdl.phone_home,
    phone_fax=mdl.phone_fax,
    phone_other=mdl.phone_other,
    tshirt_size=mdl.tshirt_size,
    notes=mdl.notes,
    last_editor=unicode(mdl.last_editor),
    id=mdl.key.integer_id(),
  )
  if mdl.last_welcome:
    s.last_welcome = mdl.last_welcome.isoformat()  # datetime, fo  if mdl.modified:
    s.modified = mdl.modified.isoformat()  # datetime, for display only
  return s

def _CaptainMessageToModel(msg, mdl):
  mdl.name = msg.name
  mdl.email = msg.email
  mdl.rooms_id = msg.rooms_id
  mdl.phone_mobile = msg.phone_mobile
  mdl.phone_work = msg.phone_work
  mdl.phone_home = msg.phone_home
  mdl.phone_fax = msg.phone_fax
  mdl.phone_other = msg.phone_other
  mdl.tshirt_size = msg.tshirt_size
  mdl.notes = msg.notes
  # can't set automatic fields
  # last_welcome modified last_editor
  return mdl

class Captain(messages.Message):
  id = messages.IntegerField(1)
  name = messages.StringField(2)
  email = messages.StringField(3)
  rooms_id = messages.StringField(4)
  phone_mobile = messages.StringField(5)
  phone_work = messages.StringField(6)
  phone_home = messages.StringField(7)
  phone_fax = messages.StringField(8)
  phone_other = messages.StringField(9)
  tshirt_size = messages.StringField(10)
  notes = messages.StringField(11)
  last_welcome = messages.StringField(12)
  modified = messages.StringField(13)
  last_editor = messages.StringField(14)
  # search_prefixes is internal only

############
# Supplier #
############

def _SupplierModelToMessage(mdl):
  s = Supplier(
    id=mdl.key.integer_id(),
    name=mdl.name,
    email=mdl.email,
    address=mdl.address,
    phone1=mdl.phone1,
    phone2=mdl.phone2,
    notes=mdl.notes,
    active=mdl.active,            
    visibility=mdl.visibility,
  )
  if mdl.since:
    s.since = mdl.since.isoformat()  # datetime, for display only
  return s

def _SupplierMessageToModel(msg, mdl):
  mdl.name = msg.name
  mdl.email = msg.email
  mdl.address = msg.address
  mdl.phone1 = msg.phone1
  mdl.phone2 = msg.phone2
  mdl.notes = msg.notes
  mdl.active = msg.active
  mdl.visibility = msg.visibility
  # can't set "since", it's automatic
  return mdl

class Supplier(messages.Message):
  name = messages.StringField(1)
  email = messages.StringField(2)
  address = messages.StringField(3)
  phone1 = messages.StringField(4)
  phone2 = messages.StringField(5)
  notes = messages.StringField(6)
  since = messages.StringField(7)
  active = messages.StringField(8)
  visibility = messages.StringField(9)
  id = messages.IntegerField(10)


############
# Site #
############

def _SiteModelToMessage(mdl):
  s = Site(
    id=mdl.key.integer_id(),
    number=mdl.number,
  )
  # Any special handling, like for user objects or datetimes
  return s

def _SiteMessageToModel(msg, mdl):
  mdl.number = msg.number
  # can't set automatic fields:
  # TODO
  return mdl

class Site(messages.Message):
  id = messages.IntegerField(1)
  number = messages.StringField(2) 


############
# OrderSheet #
############

def _OrderSheetModelToMessage(mdl):
  s = OrderSheet(
    id=mdl.key.integer_id(),
    code=mdl.code,
    name=mdl.name,
    delivery_options=mdl.delivery_options,
    default_supplier=mdl.default_supplier.integer_id(),
    visibility=mdl.visibility,
    retrieval_options=mdl.retrieval_options,
    pickup_options=mdl.pickup_options,
  )
  # any special handling, like for user objects or datetimes
  return s

def _OrderSheetMessageToModel(msg, mdl):
  mdl.code = msg.code
  mdl.name = msg.name
  mdl.delivery_options = msg.delivery_options
  mdl.default_supplier = ndb.Key(ndb_models.Supplier, msg.default_supplier)
  mdl.visibility = msg.visibility
  mdl.retrieval_options = msg.retrieval_options
  mdl.pickup_options = msg.pickup_options
  # can't set automatic fields:
  # TODO
  return mdl

class OrderSheet(messages.Message):
  id = messages.IntegerField(1)
  code = messages.StringField(2)
  name = messages.StringField(3)
  delivery_options = messages.StringField(4)
  default_supplier = messages.IntegerField(5)
  visibility = messages.StringField(6)
  retrieval_options = messages.StringField(7)
  pickup_options = messages.StringField(8)

  

# Use the multi-line string below as a template for adding models.
"""
############
# Example #
############

def _ExampleModelToMessage(mdl):
  s = Example(
    id=mdl.key.integer_id(),
    name=mdl.name,
  )
  # any special handling, like for user objects or datetimes
  return s

def _ExampleMessageToModel(msg, mdl):
  mdl.name = msg.name
  # can't set automatic fields:
  # TODO
  return mdl

class Example(messages.Message):
  id = messages.IntegerField(1)
  name = messages.StringField(2)

"""
  
basic_crud_config = (
  (Jurisdiction, ndb_models.Jurisdiction,
   _JurisdictionMessageToModel, _JurisdictionModelToMessage),
  (Staff, ndb_models.Staff,
   _StaffMessageToModel, _StaffModelToMessage),
  (Captain, ndb_models.Captain,
   _CaptainMessageToModel, _CaptainModelToMessage),
  (Supplier, ndb_models.Supplier,
   _SupplierMessageToModel, _SupplierModelToMessage),
  (Site, ndb_models.NewSite,
   _SiteMessageToModel, _SiteModelToMessage),
  (OrderSheet, ndb_models.OrderSheet,
   _OrderSheetMessageToModel, _OrderSheetModelToMessage),
#  (Example, ndb_models.Example,
# _ExampleMessageToModel, _ExampleModelToMessage),
  )

class _GeneratedCrudApi(remote._ServiceClass):  # sorry. but 'remote' used metaclass so we have to as well.
  """Metaclass for adding CRUD methods to a service, based on a config."""

  def __new__(mcs, name, bases, dct):
    """Set up mcs dict so it will have methods wrapped by remote.method.

    This is necessary to get the protorpc service to notice the methods, since
    it does so in remote._Service metaclass.
    """

    def makeBasicCrud(msg_name, msg_cls, mdl_cls, g2d, d2g):
      """Create functions for three basic CRU operations on a model.

      CRU == Create, Read, Update.  

      We don't do Delete because it may leave dangling references.

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


class RoomApi(six.with_metaclass(_GeneratedCrudApi, remote.Service)):
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
    if user and ( user.staff or user.captain ):
      return
    raise remote.ApplicationError('Must be a ROOMS user to use this API.')

  @remote.method(message_types.VoidMessage,
                 message_types.VoidMessage)
  def ehlo(self, request):
    logging.info('ehlo')
    return message_types.VoidMessage()
    
  # This needs an update for the new encoding for StaffPosition rates.  Per issue 238.
  # If it's used at all...
  @remote.method(StaffPosition,
                 GenericResponse)
  def staffposition_put(self, request):
    self._authorize_staff()
    sp = ndb_models.StaffPosition(position_name=request.position_name,
                                  hourly_rate=request.hourly_rate)
    if request.key:
      sp.key = ndb.Key(ndb_models.StaffPosition, request.key)
    sp.put()
    return GenericResponse()

  @remote.method(Program,
                 GenericResponse)  
  def program_put(self, request):
    self._authorize_staff()
    resp = GenericResponse()
    try:
      sp = ndb_models.Program(name=request.name,
                              year=request.year,
                              site_number_prefix=request.site_number_prefix,
                              status=request.status)
      sp.put()
      resp.message = 'OK'
    except Exception, e:
      resp.message = str(e)

    return resp

  @remote.method(message_types.VoidMessage,
                 Programs)  
  def program_list(self, request):
    programs = Programs()
    for p in ndb_models.Program.query():
      programs.program.append(Program(name=p.name, year=p.year))
    return programs
    
  @remote.method(message_types.VoidMessage,
                 Choices)  
  def supplier_choices(self, request):
    choices = Choices()
    for mdl in ndb_models.Supplier.query():
      choices.choice.append(Choice(id=mdl.key.integer_id(), label=mdl.name))
    return choices
  
application = service.service_mapping(RoomApi, r'/wsgi_service')

