import ndb_models
import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote


class GenericResponse(messages.Message):
  message = messages.StringField(1)


class StaffPosition(messages.Message):
    key = messages.StringField(1)
    position_name = messages.StringField(2)
    hourly_rate = messages.FloatField(3)


@endpoints.api(name='roomApi',version='v1',
               auth_level=endpoints.AUTH_LEVEL.REQUIRED,
               allowed_client_ids=[endpoints.API_EXPLORER_CLIENT_ID,],
               description='Rebuilding Together Peninsula ROOM System API')
class RoomApi(remote.Service):

    @endpoints.method(StaffPosition,
                      GenericResponse,
                      name='staffposition.put')
    def put(self, request):
        u = endpoints.get_current_user()
        sp = ndb_models.StaffPosition(position_name=request.position_name,
                                      hourly_rate=request.hourly_rate)
        if request.key:
            sp.key = request.key
        sp.put()
        return GenericResponse()


application = endpoints.api_server([RoomApi])
