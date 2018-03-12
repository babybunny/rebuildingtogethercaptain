"""API for choices that appear as parts of forms, in drop-dpwn menus."""

from google.appengine.ext import ndb

from protorpc import message_types
from protorpc import messages
from protorpc import remote
from protorpc.wsgi import service

import base_api
import ndb_models

package = 'rooms'


class Site(messages.Message):
  id = messages.IntegerField(1, required=True)

  
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
    for mdl in ndb_models.Captain.query().order(ndb_models.Captain.name):
      choices.choice.append(Choice(id=mdl.key.integer_id(), label=mdl.name))
    return choices

  @remote.method(Site, Choices)
  def captain_for_site_choices_read(self, request):
    self._authorize_user()
    choices = Choices()
    if self._user.staff:
      for mdl in ndb_models.Captain.query().order(ndb_models.Captain.name):
        choices.choice.append(Choice(id=mdl.key.integer_id(), label=mdl.name))
      return choices
      
    sitecaptain_models = list(
      ndb_models.SiteCaptain.query(ndb_models.SiteCaptain.site == ndb.Key(ndb_models.NewSite, request.id)))
    captains = ndb.get_multi(set(m.captain for m in sitecaptain_models))
    captains.sort(key=lambda c: c.name)
    for mdl in captains:
      choices.choice.append(Choice(id=mdl.key.integer_id(), label=mdl.name))
    return choices

  @remote.method(message_types.VoidMessage,
                 Choices)
  def supplier_choices_read(self, request):
    self._authorize_user()
    choices = Choices()
    for mdl in ndb_models.Supplier.query(ndb_models.Supplier.active == 'Active').order(ndb_models.Supplier.name):
      choices.choice.append(Choice(id=mdl.key.integer_id(), label=mdl.name))
    return choices

  @remote.method(message_types.VoidMessage,
                 Choices)
  def staffposition_choices_read(self, request):
    self._authorize_user()
    choices = Choices()
    for mdl in ndb_models.StaffPosition.query().order(ndb_models.StaffPosition.position_name):
      choices.choice.append(Choice(id=mdl.key.integer_id(), label=mdl.position_name))
    return choices

  @remote.method(message_types.VoidMessage,
                 Choices)
  def jurisdiction_choices_read(self, request):
    self._authorize_user()
    choices = Choices()
    for mdl in ndb_models.Jurisdiction.query().order(ndb_models.Jurisdiction.name):
      choices.choice.append(Choice(id=mdl.key.integer_id(), label=mdl.name))
    return choices

  @remote.method(message_types.VoidMessage,
                 Choices)
  def ordersheet_choices_read(self, request):
    self._authorize_user()
    choices = Choices()
    mdls = ndb_models.OrderSheet.query(ndb_models.OrderSheet.visibility != 'Inactive')
    for mdl in sorted(mdls, key=lambda m: m.name):
      choices.choice.append(Choice(id=mdl.key.integer_id(), label=mdl.name))
    return choices


application = service.service_mapping(ChoicesApi, r'/choices_api')
