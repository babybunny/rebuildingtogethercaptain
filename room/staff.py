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
    user, _ = common.GetUser()
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
  def dispatch(self):
    user, status = common.GetUser()
    if user and user.staff:    
      if not user.staff.program_selected:
        logging.info(self.request)
        return webapp2.redirect_to('SelectProgram')
      super(StaffHandler, self).dispatch()
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

def _Autocomplete(request, model_class, program_filter=False):
  prefix = str(request.get('term').lower())
  items = model_class.query()
  items.filter(model_class.search_prefixes == prefix)
  if program_filter:
    user, _ = common.GetUser()
    items.filter(model_class.program == user.program_selected)
  matches = {}
  for i in items.iter():
    label = i.Label()
    matches[label] = i.key.urlsafe()
  response = webapp2.Response(content_type='application/json')
  response.write(json.dumps(matches))
  return response


class SiteAutocomplete(StaffHandler):
  """Return JSON to autocomplete a Site ID based on a prefix."""
  def get(self):
    return _Autocomplete(self.request, ndb_models.NewSite, program_filter=True)


class CaptainAutocomplete(StaffHandler):
  """Return JSON to autocomplete a Captain."""
  def get(self):
    return _Autocomplete(self.request, ndb_models.Captain)

    
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


class SupplierList(StaffHandler):
  def get(self):
    return _EntryList(self.request, ndb_models.Supplier, 'supplier_list')

  
class Supplier(StaffHandler):
  def get(self, supplier_id=None):
    d = dict()
    if supplier_id:
      supplier_id = int(supplier_id)
      if supplier_id:
        d['supplier'] = ndb.Key(ndb_models.Supplier, supplier_id).get()
    return common.Respond(self.request, 'supplier', d)

  
class SiteJump(StaffHandler):
  def get(self):
    user, _ = common.GetUser()
    d = {'user': user}
    number = request.get('number')
    site = ndb_models.NewSite.query(ndb_models.NewSite.number == number).get()
    if site is None:
      return webapp2.redirect_to('StaffHome')
    else:
      return webapp2.redirect_to('SiteView', site.key.integer_id())
