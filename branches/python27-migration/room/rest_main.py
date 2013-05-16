import logging
import json
import StringIO

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import rest
from room import plain_models

# # monkey-patch rest 
# def json_to_xml(json_doc):
#     """Returns an xml document generated from the given json doc.

#     The appengine-rest-server form expects JSON like this
#     {"Model": {"attr1": "val1", ...}}
#     but this accepts the simpler
#     {"attr1": "val1", ...}
#     which is what AngularJS $resource module sends.
#     """
#     json_node = rest.json.load(json_doc)
#     impl = rest.minidom.getDOMImplementation()
#     xml_doc = impl.createDocument(None, 'Program', None)
#     rest.json_node_to_xml(xml_doc.documentElement, json_node)
#     return xml_doc

# rest.json_to_xml = json_to_xml


class RestDispatcherForAngularJS(rest.Dispatcher):
  def post(self, *_):
    """Convert from AngularJS input to rest.Dispatcher format.

    Angular sends {"attr1": "val1", ...} but rest.Dispatcher
    expects {"Model": {"attr1": "val1", ...}}
    """
    model_name = self.request.path.split('/')[-1]
    self.request.body = '{"%s": %s}' % (model_name, 
                                        self.request.body)
    return rest.Dispatcher.post(self, *_)
    
  def write_output(self, out):
    """Note that we patch write_output so the caching in get() still works."""
    
    model_name = self.request.path.split('/')[-1]
    out_json = json.loads(out)
    logging.info(out_json)
    new_out = json.dumps(out_json['list'][model_name])
    logging.info(new_out)
    return rest.Dispatcher.write_output(self, new_out)
  


# add a handler for REST calls
application = webapp.WSGIApplication(
    [
        ('/rest/metadata', lambda x: d),
        ('/room/rest/.*', RestDispatcherForAngularJS)
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
