"""Staff views"""

import datetime
import json
import logging
import webapp2
from google.appengine.ext import ndb

import ndb_models
import common

TEST_SITE_NUMBER = '11999ZZZ'


class SelectProgram(webapp2.RequestHandler):
  """Handler for Staff to select a program.

  This is different from other Staff handlers because it is 
  the only prerequisite to loading the StaffHome page.  So 
  it requires that the user is staff but does not require that 
  program is already selected. Bootstrapping.
  """

  def get(self):
    user, _ = common.GetUser(self.request)
    if not user and not user.staff:
      return webapp2.redirect_to('Start')
    program = self.request.get('program')
    if not program:
      what_you_are_doing = "Select a Program to work on"
      program_url_base = webapp2.uri_for('SelectProgram')
      return common.Respond(self.request, 'select_program', locals())

    if program not in common.PROGRAMS:
      return http.HttpResponseError('program %s not in PROGRAMS' % program)
    user.staff.program_selected = program
    user.staff.put()
    return webapp2.redirect_to('StaffHome')


class StaffHandler(webapp2.RequestHandler):
  """Handler base class that ensures the user meets Staff view prerequisites:
  - user is logged in
  - user matches an existing Staff record
  - Staff record has a selected Program
  """
  def dispatch(self, *a, **k):
    user, status = common.GetUser(self.request)
    if user and user.staff:    
      if not user.staff.program_selected:
        logging.info(self.request)
        return webapp2.redirect_to('SelectProgram')
      super(StaffHandler, self).dispatch(*a, **k)
    else:
      return webapp2.redirect_to('Start')

    
class StaffHome(StaffHandler):
  def get(self):
    order_sheets = list(ndb_models.OrderSheet.query())
    order_sheets.sort(key=lambda x: x.name)
    jurisdictions = list(ndb_models.Jurisdiction.query())
    jurisdictions.sort(key=lambda x: x.name)
    d = {'order_sheets': order_sheets,
         'test_site_number': TEST_SITE_NUMBER,
         'jurisdictions': jurisdictions,
         }
    return common.Respond(self.request, 'staff_home', d)


class AutocompleteHandler(StaffHandler):
  model_class = None
  program_filter = False

  def get(self):
    prefix = str(self.request.get('term').lower())
    logging.info(prefix)
    items = self.model_class.query()
    items.filter(self.model_class.search_prefixes == prefix)
    if self.program_filter:
      user, _ = common.GetUser(self.request)
      items.filter(self.model_class.program == user.program_selected)
    matches = {}
    for i in items.iter():
      label = i.Label()
      matches[label] = str(i.key.integer_id())

    self.response.content_type='application/json'
    self.response.write(json.dumps(matches))


class SiteAutocomplete(AutocompleteHandler):
  """Return JSON to autocomplete a Site ID based on a prefix."""
  model_class = ndb_models.NewSite
  program_filter = True


class CaptainAutocomplete(AutocompleteHandler):
  """Return JSON to autocomplete a Captain."""
  model_class = ndb_models.Captain
  program_filter = False


class SiteView(StaffHandler):
  def get(self, id=None):
    if id:
      id = int(id)
      site = ndb.Key(ndb_models.NewSite, id).get()
    d = dict(
      map_width=common.MAP_WIDTH, map_height=common.MAP_HEIGHT
    )
    entries = [site]
    d['site_list_detail'] = True
    d['start_new_order_submit'] = common.START_NEW_ORDER_SUBMIT
    d['entries'] = entries
    order_sheets = ndb_models.OrderSheet.query().order(ndb_models.OrderSheet.name)
    d['order_sheets'] = order_sheets
    return common.Respond(self.request, 'site_list_one', d)


class SitesAndCaptains(StaffHandler):
  """Show all Sites and their associated captains in a big list"""
  def get(self):
    user, _ = common.GetUser(self.request)
    if not user.program_selected:
      webapp2.abort(400)
    query = ndb_models.NewSite.query(ndb_models.NewSite.program == user.program_selected)
    query.order(ndb_models.NewSite.number)
    entries = list(query)
    sitecaptains_by_site = {}
    # TODO: this is fetching too many - we only need those for the current
    # program.  use ancestor?
    for sc in ndb_models.SiteCaptain.query():
      sitecaptains_by_site.setdefault(sc.site.integer_id(), []).append(sc)
    for s in entries:
      k = s.key.integer_id()
      if k in sitecaptains_by_site:
        s.sitecaptains = sitecaptains_by_site[k]
    d = {'entries': entries, 'num_entries': len(entries), 'user': user,
         'sitecaptains_by_site': sitecaptains_by_site}
    return common.Respond(self.request, 'site_list', d)

    
def _EntryList(request, model_cls, template, params=None, query=None):
  """Generic helper method to perform a list view.

  This method does not enforce any authorization. It should be called after 
  authorization is successful..

  Template should iterate over a list called 'entries'.
  Sorts entries on their 'name' attribute (which they must have).

  Args:
    request: the request object
    model_cls: the class of model, like models.Captain
    template: name of template file, like 'captain_list'
    params: dict of more template parameters
    query: db.Query object to use, if not model_cls.query()
    """
  if query is None:
    query = model_cls.query()
  entries = list(query)
  entries.sort(key=lambda x: x.name)
  d = {'entries': entries, 'num_entries': len(entries),
       'cls': model_cls,
       'model_cls_name': model_cls.__name__}
  if params:
    d.update(params)
  return common.Respond(request, template, d)


class EditView(StaffHandler):
  model_class = None
  template_value = None
  template_file = None

  def get(self, id=None):
    d = dict(list_uri=webapp2.uri_for(self.list_view),
             type=self.template_value)
    if id:
      id = int(id)
      d[self.template_value] = ndb.Key(self.model_class, id).get()
    return common.Respond(self.request, self.template_file, d)
  

class StaffList(StaffHandler):
  def get(self):
    return _EntryList(self.request, ndb_models.Staff, 'staff_list')

class Staff(EditView):
  model_class = ndb_models.Staff
  list_view = 'StaffList'
  template_value = 'staff'
  template_file = 'simple_form'


class CaptainList(StaffHandler):
  def get(self):
    return _EntryList(self.request, ndb_models.Captain, 'captain_list')

class Captain(EditView):
  model_class = ndb_models.Captain
  list_view = 'CaptainList'
  template_value = 'captain'
  template_file = 'simple_form'
  

class SupplierList(StaffHandler):
  def get(self):
    return _EntryList(self.request, ndb_models.Supplier, 'supplier_list')

class Supplier(EditView):
  model_class = ndb_models.Supplier
  list_view = 'SupplierList'
  template_value = 'supplier'
  template_file = 'simple_form'

  
# SiteList is done by custom view SitesAndCaptains

class Site(EditView):
  model_class = ndb_models.NewSite
  list_view = 'SitesAndCaptains'
  template_value = 'site'
  template_file = 'simple_form'

  
"""
class ExampleList(StaffHandler):
  def get(self):
    return _EntryList(self.request, ndb_models.Example, 'example_list')

class Example(EditView):
  model_class = ndb_models.Example
  list_view = 'ExampleList'
  template_value = 'example'
  template_file = 'simple_form'
"""
  


