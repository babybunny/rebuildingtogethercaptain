
import endpoints
from google.appengine.ext import ndb
from protorpc import remote

from endpoints_proto_datastore.ndb import EndpointsModel

class Program(EndpointsModel):
    """Identifies a program like "National Rebuilding Day".
    
    Programs with status 'Active' will be visible to Captains.
    
    Keys are shorthand like "2012 NRD".
    """
    year = ndb.IntegerProperty()
    name = ndb.StringProperty()
    site_number_prefix = ndb.StringProperty()
    status = ndb.StringProperty(choices=('Active', 'Inactive'), 
                                default='Inactive')

@endpoints.api(name='roomAutoApi', version='v1', 
               description='ROOMS Automatic API')

class RoomAutoApi(remote.Service):
    @Program.method(path='program', http_method='POST', name='program.insert')
    def ProgramInsert(self, my_model):
        my_model.put()
        return my_model

    @Program.query_method(path='programs', name='program.list')
    def ProgramList(self, query):
        return query


application = endpoints.api_server([RoomAutoApi], restricted=False)
