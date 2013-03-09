
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import rest
from room import plain_models

# add a handler for REST calls
application = webapp.WSGIApplication(
    [
        ('/rest/metadata', lambda x: d),
        ('/room/rest/.*', rest.Dispatcher)
        ],
    debug=True
    )

# configure the rest dispatcher to know what prefix to expect on request
# urls
rest.Dispatcher.base_url = '/room/rest'
# add specific models (with given names)
rest.Dispatcher.model_handlers = {}
rest.Dispatcher.add_models({
        'Program' : plain_models.Program,
        })


class RoomAuthenticator(rest.Authenticator):
    def authenticate(self, dispatcher):
        if users.GetCurrentUser():
            return
        dispatcher.forbidden()
        

# rest.Dispatcher.authenticator = RoomAuthenticator()
# rest.Dispatcher.authorizer = RoomAuthorizer()

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
