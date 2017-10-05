
from google.appengine.ext import ndb
from protorpc import message_types
from protorpc import messages
from protorpc import remote
from protorpc.wsgi import service

import ndb_models

package = 'rooms'

class Choice(messages.Message):
  id = messages.IntegerField(1, required=True)
  label = messages.StringField(2)


class Choices(messages.Message):
  choice = messages.MessageField(Choice, 1, repeated=True)


class ChoicesApi(remote.Service):
  """Protorpc service implementing APIs that exist to populate
  drop-down selections in UI.  Used when you're editing a ROOM model
  that has foreign keys.
  """

  # TODO: merge with similar methods in wsgi_service.py
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

  @remote.method(message_types.VoidMessage,
                 Choices)
  def captain_choices_read(self, request):
    choices = Choices()
    for mdl in ndb_models.Captain.query().order(ndb_models.Supplier.name):
      choices.choice.append(Choice(id=mdl.key.integer_id(), label=mdl.name))
    return choices

  @remote.method(message_types.VoidMessage,
                 Choices)
  def supplier_choices_read(self, request):
    choices = Choices()
    for mdl in ndb_models.Supplier.query(ndb_models.Supplier.active == 'Active').order(ndb_models.Supplier.name):
      choices.choice.append(Choice(id=mdl.key.integer_id(), label=mdl.name))
    return choices

  @remote.method(message_types.VoidMessage,
                 Choices)
  def staffposition_choices_read(self, request):
    choices = Choices()
    for mdl in ndb_models.StaffPosition.query().order(ndb_models.StaffPosition.position_name):
      choices.choice.append(Choice(id=mdl.key.integer_id(), label=mdl.position_name))
    return choices

  @remote.method(message_types.VoidMessage,
                 Choices)
  def jurisdiction_choices_read(self, request):
    choices = Choices()
    for mdl in ndb_models.Jurisdiction.query().order(ndb_models.Jurisdiction.name):
      choices.choice.append(Choice(id=mdl.key.integer_id(), label=mdl.name))
    return choices

  @remote.method(message_types.VoidMessage,
                 Choices)
  def ordersheet_choices_read(self, request):
    choices = Choices()
    for mdl in ndb_models.OrderSheet.query().order(ndb_models.OrderSheet.name):
      choices.choice.append(Choice(id=mdl.key.integer_id(), label=mdl.name))
    return choices


application = service.service_mapping(ChoicesApi, r'/choices_api')
