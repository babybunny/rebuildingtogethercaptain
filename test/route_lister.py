"""List routes of a webapp2 app.

https://stackoverflow.com/questions/13078892/in-webapp2-how-can-i-get-a-list-of-all-route-uris
"""
import main
from room import ndb_models

ROUTE_TEST_DATA = {
  # 'Staff': {'model': ndb_models.Staff}
  ''
}

class RouteLister(object):

  def __init__(self, router=main.login_required):
    self._default_router = router
    self.route_data = None
    self._populate()

  def _get_routes(self, router=None):
    """get list of routes from either a router object or a PathPrefixRoute object,
    because they were too stupid to give them the same interface.
    """
    router = router or self._default_router
    if hasattr(router, 'match_routes'):
      return router.match_routes
    else:
      return list(router.get_routes())

  def _get_doc(self, handler, method):
    """get the doc from the method if there is one,
    otherwise get the doc from the handler class."""
    if method:
      return getattr(handler,method).__doc__
    else:
      return handler.__doc__

  def _populate(self):
    self.route_data = []
    for i in self._get_routes():
      if hasattr(i, 'handler'):
        # I think this means it's a route, not a path prefix
        cur_template = i.template
        cur_handler  = i.handler
        cur_method   = i.handler_method
        cur_doc      = self._get_doc(cur_handler,cur_method)
        cur_test_data = ROUTE_TEST_DATA.get(i.name)
        r = {'template':cur_template,
             'handler':cur_handler,
             'method':cur_method,
             'doc':cur_doc,
             'name': i.name,
             'test_data': cur_test_data}
        self.route_data.append(r)
      else:
        r = self._get_routes(i)
        self.route_data.extend(r)
