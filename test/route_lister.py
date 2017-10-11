"""List routes of a webapp2 app.

https://stackoverflow.com/questions/13078892/in-webapp2-how-can-i-get-a-list-of-all-route-uris
"""
from gae import main


class RouteLister(object):

  def __init__(self, router=main.app.router):
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

  def _route_to_dict(self, route):
    cur_template = route.template
    cur_handler = route.handler
    cur_method = route.handler_method
    cur_doc = self._get_doc(cur_handler, cur_method)
    r = {'template': cur_template,
         'handler': cur_handler,
         'method': cur_method,
         'allowed_methods': route.methods or ['GET'],
         'doc': cur_doc,
         'name': route.name,
         'url_params': getattr(route, 'url_params', None),
         'post_data': getattr(route, 'post_data', None), }
    return r

  def _populate(self):
    self.route_data = []
    for route in self._get_routes():
      if hasattr(route, 'handler'):
        self.route_data.append(self._route_to_dict(route))
      else:
        route_data_list = map(self._route_to_dict, self._get_routes(route))
        self.route_data.extend(route_data_list)
