"""API for StaffPositions and their (hourly,mileage) info."""

from google.appengine.ext import ndb

from protorpc import message_types
from protorpc import messages
from protorpc import remote
from protorpc.wsgi import service

import base_api
import ndb_models
from protorpc_messages import SimpleId

package = 'rooms'


class RateAfterDate(messages.Message):
  date = messages.StringField(1)
  rate = messages.FloatField(2)


class StaffPosition(messages.Message):
  id = messages.IntegerField(1)
  position_name = messages.StringField(2)
  hourly_rates = messages.MessageField(RateAfterDate, 3, repeated=True)
  mileage_rates = messages.MessageField(RateAfterDate, 4, repeated=True)


class StaffpositionApi(base_api.BaseApi):

  def staffposition_message_to_model(self, msg, mdl):
    if not msg.position_name:
      raise remote.ApplicationError('Position name is required')
    mdl.position_name = msg.position_name
    mdl.hourly_rate_after_date = [
      '{} {:.2f}'.format(r.date, r.rate) for r in msg.hourly_rates if r.date and r.rate]
    mdl.mileage_rate_after_date = [
      '{} {:.2f}'.format(r.date, r.rate) for r in msg.mileage_rates if r.date and r.rate]
    return mdl

  @remote.method(StaffPosition, message_types.VoidMessage)
  def staffposition_create(self, request):
    self._authorize_staff()
    if request.id:
      raise remote.ApplicationError('must not have id in create')
    mdl = ndb_models.StaffPosition()
    self.staffposition_message_to_model(request, mdl)
    mdl.put()
    return message_types.VoidMessage()

  @remote.method(StaffPosition, message_types.VoidMessage)
  def staffposition_update(self, request):
    self._authorize_staff()
    if not request.id:
      raise remote.ApplicationError('id is required to update staffposition')
    mdl = ndb.Key(ndb_models.StaffPosition, request.id).get()
    if not mdl:
      raise remote.ApplicationError('No staffposition fournd with key {}'.format(request.id))
    self.staffposition_message_to_model(request, mdl)
    mdl.put()
    return message_types.VoidMessage()

  @remote.method(SimpleId, StaffPosition)
  def staffposition_read(self, request):
    self._authorize_staff()
    if not request.id:
      raise remote.ApplicationError('id is required to read staffposition')
    mdl = ndb.Key(ndb_models.StaffPosition, request.id).get()
    if not mdl:
      raise remote.ApplicationError('No staffposition found with key {}'.format(
        request.id))
    res = StaffPosition(position_name=mdl.position_name)
    for d, r in (dr.split() for dr in mdl.mileage_rate_after_date):
      res.mileage_rates.append(RateAfterDate(date=d, rate=float(r)))
    for d, r in (dr.split() for dr in mdl.hourly_rate_after_date):
      res.hourly_rates.append(RateAfterDate(date=d, rate=float(r)))
    return res

application = service.service_mapping(StaffpositionApi, r'/staffposition_api')
