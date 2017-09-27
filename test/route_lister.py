"""List routes of a webapp2 app.

https://stackoverflow.com/questions/13078892/in-webapp2-how-can-i-get-a-list-of-all-route-uris
"""

def get_route_list(router):
  """
  Get a nested list of all the routes in the app's router
  """
  def get_routes(r):
    """get list of routes from either a router object or a PathPrefixRoute object,
    because they were too stupid to give them the same interface.
    """
    if hasattr(r, 'match_routes'):
      return r.match_routes
    else:
      return list(r.get_routes())

  def get_doc(handler, method):
    """get the doc from the method if there is one,
    otherwise get the doc from the handler class."""
    if method:
      return getattr(handler,method).__doc__
    else:
      return handler.__doc__

  routes=[]
  for i in get_routes(router):
    assert hasattr(i, 'handler')  # I think this means it's a route, not a path prefix
    cur_template = i.template
    cur_handler  = i.handler
    cur_method   = i.handler_method
    cur_doc      = get_doc(cur_handler,cur_method)
    r={'template':cur_template, 'handler':cur_handler, 'method':cur_method, 'doc':cur_doc, 'name': i.name}
    routes.append(r)

  return routes

