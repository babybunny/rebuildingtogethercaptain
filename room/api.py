import common
import ndb_models
import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

from google.appengine.api import users
from google.appengine.ext import ndb


class GenericResponse(messages.Message):
  message = messages.StringField(1)
  
class StaffPosition(messages.Message):
  key = messages.IntegerField(1)
  position_name = messages.StringField(2)
  hourly_rate = messages.FloatField(3)
  
class OauthUser(messages.Message):
  email = messages.StringField(1)

class User(messages.Message):
  name = messages.StringField(1)
  status = messages.StringField(2)
  oauth_email = messages.StringField(3)
  server_email = messages.StringField(4)
  staff_key = messages.StringField(5)
  captain_key = messages.StringField(6)
  
class Program(messages.Message):
  year = messages.IntegerField(1)
  name = messages.StringField(2)
  site_number_prefix = messages.StringField(3)
  status = messages.StringField(4)

class Programs(messages.Message):
  program = messages.MessageField(Program, 1, repeated=True)


def _authorize_staff():
  """Simply call this to ensure that the user has a Staff record.
  
  Raises:
    endpoints.UnauthorizedException if the user is not Staff.
  """
  if os.environ['SERVER_SOFTWARE'].startswith('Development'):
    return
  current_user = endpoints.get_current_user()
  if current_user is None:
    raise endpoints.UnauthorizedException('Invalid token.')
  staff = ndb_models.Staff.query(
    ndb_models.Staff.email == current_user.email().lower()).get()
  if not staff:
    raise endpoints.UnauthorizedException(
      'Must be staff to use this API.')


@endpoints.api(name='roomApi',version='v1',
               auth_level=endpoints.AUTH_LEVEL.REQUIRED,
               allowed_client_ids=[
    endpoints.API_EXPLORER_CLIENT_ID,
    '1093814363166-dp6d5juof62nf0siaja08fabqsh8ber3.apps.googleusercontent.com'],
               description='Rebuilding Together Peninsula ROOM System API')
class RoomApi(remote.Service):

  # This needs an update for the new encoding for StaffPosition rates.  Per issue 238.
  # If it's used at all...
  @endpoints.method(StaffPosition,
                    GenericResponse,
                    name='staffposition.put')
  def staffposition_put(self, request):
    _authorize_staff()
    sp = ndb_models.StaffPosition(position_name=request.position_name,
                                  hourly_rate=request.hourly_rate)
    if request.key:
      sp.key = ndb.Key(ndb_models.StaffPosition, request.key)
    sp.put()
    return GenericResponse()

  @endpoints.method(Program,
                    GenericResponse,
                    name='program.put')
  def program_put(self, request):
    _authorize_staff()
    sp = ndb_models.Program(name=request.name,
                            year=request.year,
                            site_number_prefix=request.site_number_prefix,
                            status=request.status)
    sp.put()
    return GenericResponse()

  @endpoints.method(message_types.VoidMessage,
                    Programs,
                    http_method='GET',
                    name='program.list')
  def program_list(self, request):
    programs = Programs()
    for p in ndb_models.Program.query():
      programs.program.append(Program(name=p.name, year=p.year))
    return programs

  @endpoints.method(OauthUser,
                    User,
                    http_method='GET',
                    name='current_user.list')
  def current_user_get(self, request):
    res = User()
    e_u = endpoints.get_current_user()
    if e_u:
      res.oauth_email = e_u.email()
    c_u, res.status = common.GetUser()
    if c_u.staff:
      res.staff_key = c_u.staff.key.urlsafe()
      
    return res

application = endpoints.api_server([RoomApi])
