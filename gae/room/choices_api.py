
from google.appengine.ext import ndb
from protorpc import message_types
from protorpc import messages
from protorpc import remote
from protorpc.wsgi import service

import base_api
import models_v2

package = 'rooms'


class Choice(messages.Message):
  id = messages.IntegerField(1, required=True)
  label = messages.StringField(2)


class Choices(messages.Message):
  choice = messages.MessageField(Choice, 1, repeated=True)


class ChoicesApi(base_api.BaseApi):
  """Protorpc service implementing APIs that exist to populate
  drop-down selections in UI.  Used when you're editing a ROOM model
  that has foreign keys.
  """

  @remote.method(message_types.VoidMessage,
                 Choices)
  def captain_choices_read(self, request):
    self._authorize_staff()
    choices = Choices()
    for mdl in models_v2.Captain.query().order(models_v2.Captain.name):
      choices.choice.append(Choice(id=mdl.key.integer_id(), label=mdl.name))
    return choices

  @remote.method(message_types.VoidMessage,
                 Choices)
  def supplier_choices_read(self, request):
    self._authorize_staff()
    choices = Choices()
    for mdl in models_v2.Supplier.query(models_v2.Supplier.active == 'Active').order(models_v2.Supplier.name):
      choices.choice.append(Choice(id=mdl.key.integer_id(), label=mdl.name))
    return choices

  @remote.method(message_types.VoidMessage,
                 Choices)
  def staffposition_choices_read(self, request):
    self._authorize_staff()
    choices = Choices()
    for mdl in models_v2.StaffPosition.query().order(models_v2.StaffPosition.position_name):
      choices.choice.append(Choice(id=mdl.key.integer_id(), label=mdl.position_name))
    return choices

  @remote.method(message_types.VoidMessage,
                 Choices)
  def jurisdiction_choices_read(self, request):
    self._authorize_staff()
    choices = Choices()
    for mdl in models_v2.Jurisdiction.query().order(models_v2.Jurisdiction.name):
      choices.choice.append(Choice(id=mdl.key.integer_id(), label=mdl.name))
    return choices

  @remote.method(message_types.VoidMessage,
                 Choices)
  def ordersheet_choices_read(self, request):
    self._authorize_staff()
    choices = Choices()
    for mdl in models_v2.OrderSheet.query().order(models_v2.OrderSheet.name):
      choices.choice.append(Choice(id=mdl.key.integer_id(), label=mdl.name))
    return choices


application = service.service_mapping(ChoicesApi, r'/choices_api')
