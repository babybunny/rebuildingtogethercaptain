"""API for staffpositions and their hourly and mileage information."""

from google.appengine.ext import ndb

from protorpc import message_types
from protorpc import messages
from protorpc import remote
from protorpc.wsgi import service

import base_api
import ndb_models
import protorpc_messages

package = 'rooms'


class RateAfterDate(messages.Message):
  date = messages.StringField(1)
  rate = messages.FloatField(2)


class StaffPosition(messages.Message):
  id = messages.IntegerField(1)
  position_name = messages.StringField(2)
  hourly_rates = messages.MessageField(RateAfterDate, 3, repeated=True)
  mileage_rates = messages.MessageField(RateAfterDate, 4, repeated=True)


def RateAfterDateMessageToMdlString(msg):
  if not msg.date:
    raise remote.ApplicationError('Validation Error: Missing Date')
  if msg.rate < 0:
    raise remote.ApplicationError('Validation Error: Missing Rate')
  return '{} {:.2f}'.format(msg.date, msg.rate)


def RateAfterDateMdlStringToMessage(s):
  dt, rt = s.split()
  return RateAfterDate(date=dt, rate=float(rt))


def StaffPositionMessageToModel(msg, mdl):
  if not msg.position_name:
    raise remote.ApplicationError('position name is required')
  mdl.position_name = msg.position_name
  mdl.mileage_rate_after_date = list(RateAfterDateMessageToMdlString(s) for s in msg.mileage_rates)
  mdl.hourly_rate_after_date = list(RateAfterDateMessageToMdlString(s) for s in msg.hourly_rates)
  return mdl


def StaffPositionModelToMessage(mdl):
  s = StaffPosition(
    position_name=mdl.position_name,
    mileage_rates=list(RateAfterDateMdlStringToMessage(s) for s in mdl.mileage_rate_after_date),
    hourly_rates=list(RateAfterDateMdlStringToMessage(s) for s in mdl.hourly_rate_after_date)
    )
  return s


class StaffpositionApi(base_api.BaseApi):

  @remote.method(StaffPosition, message_types.VoidMessage)
  def staffposition_create(self, request):
    self._authorize_staff()
    if request.id:
      raise remote.ApplicationError('must not have id in create')
    mdl = StaffPositionMessageToModel(request, ndb_models.StaffPosition())
    mdl.put()
    return message_types.VoidMessage()

  @remote.method(protorpc_messages.SimpleId, StaffPosition)
  def staffposition_read(self, request):
    self._authorize_staff()
    if not request.id:
      raise remote.ApplicationError('id is required')
    mdl = ndb.Key(ndb_models.StaffPosition, request.id).get()
    if not mdl:
      raise remote.ApplicationError(
        'No staff position found with key {}'.format(request.id))
    return StaffPositionModelToMessage(mdl)

  @remote.method(StaffPosition, message_types.VoidMessage)
  def staffposition_update(self, request):
    self._authorize_staff()
    if not request.id:
      raise remote.ApplicationError('id is required for update')
    mdl = ndb.Key(ndb_models.StaffPosition, request.id).get()
    if not mdl:
      raise remote.ApplicationError(
        'No staff position found with key {}'.format(request.id))
    mdl = StaffPositionMessageToModel(request, mdl)
    mdl.put()
    return message_types.VoidMessage()

application = service.service_mapping(StaffpositionApi, r'/staffposition_api')
