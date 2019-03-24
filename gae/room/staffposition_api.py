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


class StaffpositionApi(base_api.BaseApi):
  def create_rate_after_date_string(self, dt, rt):
    if not(dt) or rt is None:
      raise remote.ApplicationError('Invalid date rate pair  %r %r' % (dt, rt))
    else:
      return " ".join([dt, str(rt)])

  @remote.method(StaffPosition, message_types.VoidMessage)
  def staffposition_create(self, request):
    self._authorize_staff()
    print request
    if request.id:
      raise remote.ApplicationError('must not have id in create')
    if not request.position_name:
      raise remote.ApplicationError('position name is required')
    mdl = ndb_models.StaffPosition(position_name=request.position_name)
    if len(request.hourly_rates):
      mdl.hourly_rate_after_date = [self.create_rate_after_date_string(h.date,
                                    h.rate) for h in request.hourly_rates if (
                                    h.date or h.rate)]
    if len(request.mileage_rates):
      mdl.mileage_rate_after_date = [self.create_rate_after_date_string(m.date,
                                     m.rate) for m in request.mileage_rates if (
                                     m.date or m.rate)]
    mdl.put()
    return message_types.VoidMessage()

  @remote.method(protorpc_messages.SimpleId, StaffPosition)
  def staffposition_read(self, request):
    self._authorize_staff()
    mdl = ndb.Key(ndb_models.StaffPosition, request.id).get()
    res = StaffPosition(position_name=mdl.position_name)
    for rad in mdl.mileage_rate_after_date:
      d, r = rad.split()
      res.mileage_rates.append(RateAfterDate(date=d, rate=float(r)))
    for rad in mdl.hourly_rate_after_date:
      d, r = rad.split()
      res.hourly_rates.append(RateAfterDate(date=d, rate=float(r)))
    return res

application = service.service_mapping(StaffpositionApi, r'/staffposition_api')
