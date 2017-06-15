import logging
import os

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

############
# Supplier #
############

def _SupplierModelToMessage(mdl):
  s = Supplier(
    name=mdl.name,
    email=mdl.email,
    address=mdl.address,
    phone1=mdl.phone1,
    phone2=mdl.phone2,
    notes=mdl.notes,
    active=mdl.active,            
    visibility=mdl.visibility,
    id=mdl.key.integer_id(),
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

#########
# Captain #
#########

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
    last_editor=mdl.last_editor,
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

class RoomApi(remote.Service):

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
    
  @remote.method(SimpleId, Supplier)
  def supplier_read(self, request):
    self._authorize_user()
    mdl = ndb.Key(ndb_models.Supplier, request.id).get()
    if not mdl:
      raise remote.ApplicationError(
        'No Supplier found with key %s' % request.id)    
    return _SupplierModelToMessage(mdl)
  
  @remote.method(Supplier, Supplier)
  def supplier_create(self, request):
    self._authorize_staff()
    if request.id:
      raise remote.ApplicationError(
        'Must not include id with create requests')
    mdl = ndb_models.Supplier()
    _SupplierMessageToModel(request, mdl)
    mdl.put()
    return _SupplierModelToMessage(mdl)

  @remote.method(Supplier, Supplier)
  def supplier_update(self, request):
    self._authorize_staff()
    if not request.id:
      raise remote.ApplicationError('id is required')
    mdl = ndb.Key(ndb_models.Supplier, request.id).get()
    if not mdl:
      raise remote.ApplicationError(
        'No Supplier found with key %s' % request.id)

    _SupplierMessageToModel(request, mdl)
    mdl.put()
    return _SupplierModelToMessage(mdl)

  @remote.method(SimpleId, Staff)
  def staff_read(self, request):
    self._authorize_staff()
    if not request.id:
      raise remote.ApplicationError('id is required')
    mdl = ndb.Key(ndb_models.Staff, request.id).get()
    if not mdl:
      raise remote.ApplicationError(
        'No Staff found with key %s' % request.id)    
    return _StaffModelToMessage(mdl)
  
  @remote.method(Staff, Staff)
  def staff_create(self, request):
    self._authorize_staff()
    if request.id:
      raise remote.ApplicationError(
        'Must not include id with create requests')
    mdl = ndb_models.Staff()
    _StaffMessageToModel(request, mdl)
    mdl.put()
    return _StaffModelToMessage(mdl)

  @remote.method(Staff, Staff)
  def staff_update(self, request):
    self._authorize_staff()
    if not request.id:
      raise remote.ApplicationError('id is required')
    mdl = ndb.Key(ndb_models.Staff, request.id).get()
    if not mdl:
      raise remote.ApplicationError(
        'No Staff found with key %s' % request.id)

    _StaffMessageToModel(request, mdl)
    mdl.put()
    return _StaffModelToMessage(mdl)

  @remote.method(SimpleId, Captain)
  def captain_read(self, request):
    self._authorize_staff()
    if not request.id:
      raise remote.ApplicationError('id is required')
    mdl = ndb.Key(ndb_models.Captain, request.id).get()
    if not mdl:
      raise remote.ApplicationError(
        'No Captain found with key %s' % request.id)    
    return _CaptainModelToMessage(mdl)
  
  @remote.method(Captain, Captain)
  def captain_create(self, request):
    self._authorize_staff()
    if request.id:
      raise remote.ApplicationError(
        'Must not include id with create requests')
    mdl = ndb_models.Captain()
    _CaptainMessageToModel(request, mdl)
    mdl.put()
    return _CaptainModelToMessage(mdl)

  @remote.method(Captain, Captain)
  def captain_update(self, request):
    self._authorize_staff()
    if not request.id:
      raise remote.ApplicationError('id is required')
    mdl = ndb.Key(ndb_models.Captain, request.id).get()
    if not mdl:
      raise remote.ApplicationError(
        'No Captain found with key %s' % request.id)

    _CaptainMessageToModel(request, mdl)
    mdl.put()
    return _CaptainModelToMessage(mdl)

  

application = service.service_mapping(RoomApi, r'/wsgi_service')
logging.info(RoomApi.all_remote_methods())
