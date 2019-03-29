"""API for StaffPositions and their (hourly,mileage) info."""

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


class StaffpositionApi(base_api.BaseApi):

  def _staffposition_put(self, request, staffposition=None):
    if not request.position_name:
      raise remote.ApplicationError('Position name is required')
    staffposition.position_name = request.position_name
    staffposition.hourly_rate_after_date = [
        '{} {:.2f}'.format(r.date, r.rate)
        for r in request.hourly_rates
        if r.date and r.rate]
    staffposition.mileage_rate_after_date = [
        '{} {:.2f}'.format(r.date, r.rate)
        for r in request.mileage_rates
        if r.date and r.rate]
    staffposition.put()

  @remote.method(StaffPosition, message_types.VoidMessage)
  def staffposition_create(self, request):
    self._authorize_user()
    if request.id:
      raise remote.ApplicationError('must not have id in create')
    staffposition = ndb_models.StaffPosition()
    self._staffposition_put(request, staffposition)
    return message_types.VoidMessage()

  @remote.method(StaffPosition, message_types.VoidMessage)
  def staffposition_update(self, request):
    self._authorize_user()
    if not(request.id):
      raise remote.ApplicationError('id is required to update staffposition')
    staffposition = ndb.Key(ndb_models.StaffPosition, request.id).get()
    self._staffposition_put(request, staffposition)
    return message_types.VoidMessage()

  @remote.method(protorpc_messages.SimpleId, StaffPosition)
  def staffposition_read(self, request):
    self._authorize_user()
    if not(request.id):
      raise remote.ApplicationError('id is required to read staffposition')
    mdl = ndb.Key(ndb_models.StaffPosition, request.id).get()
    res = StaffPosition(position_name=mdl.position_name)
    for d, r in (dr.split() for dr in mdl.mileage_rate_after_date):
      res.mileage_rates.append(RateAfterDate(date=d, rate=float(r)))
    for d, r in (dr.split() for dr in mdl.hourly_rate_after_date):
      res.hourly_rates.append(RateAfterDate(date=d, rate=float(r)))
    return res

application = service.service_mapping(StaffpositionApi, r'/staffposition_api')
