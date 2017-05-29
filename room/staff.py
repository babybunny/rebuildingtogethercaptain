"""Staff views"""

import datetime
import json
import logging
import webapp2
from google.appengine.api import images
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import taskqueue
from google.appengine.ext import deferred
from google.appengine.ext.webapp import template

import ndb_models
import common

TEST_SITE_NUMBER = '11999ZZZ'


def FindHome(user, default='/'):
  """Return path of user's home page, or a default page."""
  if user and user.email():
    email = user.email().lower()
    staff = models.Staff.all().filter('email = ', email).get()
    if staff:
      staff.last_welcome = datetime.datetime.now()
      staff.put()
      return urlresolvers.reverse(StaffHome)

    captain = models.Captain.all().filter('email = ', email).get()
    if captain:
      captain.last_welcome = datetime.datetime.now()
      captain.put()
      return urlresolvers.reverse(views.CaptainHome)

  logging.info('Can not find Captain or Staff for user: %s' % user)

  return default


def GoHome(request):
  user = users.GetCurrentUser()
  return http.HttpResponseRedirect(FindHome(user))


def StaffHome(request):
  user, status = common.GetUser()
  if not user.staff:
    return webapp2.redirect_to('Start')
  if not user.staff.program_selected:
    return webapp2.redirect_to('SelectProgram')
  # http.HttpResponseRedirect(urlresolvers.reverse(SelectProgram))
  order_sheets = list(ndb_models.OrderSheet.query())
  order_sheets.sort(key=lambda x: x.name)
  jurisdictions = list(ndb_models.Jurisdiction.query())
  jurisdictions.sort(key=lambda x: x.name)
  d = {'order_sheets': order_sheets,
       'test_site_number': TEST_SITE_NUMBER,
       'jurisdictions': jurisdictions,
       }
  return common.Respond(request, 'staff_home', d)


# class SelectProgram(webapp2.RequestHandler):

def SelectProgram(request):
    user, _ = common.GetUser()
    if not user.staff:
      return webapp2.redirect_to('Main')
    program = request.get('program')
    if not program:
      what_you_are_doing = "Select a Program to work on"
      program_url_base = webapp2.uri_for('SelectProgram')
      return common.Respond(request, 'select_program', locals())

    if program not in common.PROGRAMS:
      return http.HttpResponseError('program %s not in PROGRAMS' % program)
    user.staff.program_selected = program
    user.staff.put()
    return webapp2.redirect_to('StaffHome')


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


def SiteAutocomplete(request):
  """Return JSON to autocomplete a Site ID based on a prefix."""
  return _Autocomplete(request, ndb_models.Site, program_filter=True)


def CaptainAutocomplete(request):
  """Return JSON to autocomplete a Captain."""
  return _Autocomplete(request, ndb_models.Captain)


def SiteJump(request):
  user, _ = common.GetUser()
  d = {'user': user}
  number = request.GET['number']
  site = models.NewSite.all().filter('number = ', number).get()
  if site is None:
    return http.HttpResponseRedirect(
        urlresolvers.reverse(StaffHome))
  else:
    return http.HttpResponseRedirect(
        urlresolvers.reverse(views.SiteView, args=[site.key().id()]))


def SitesWithoutOrder(request, order_sheet_id):
  user, _ = common.GetUser()
  order_sheet = models.OrderSheet.get_by_id(int(order_sheet_id))
  if order_sheet is None:
    return http.HttpResponseNotFound(
        'No order_sheet exists with that key (%r)' % order_sheet_id)
  query = models.NewSite.all()
  query.filter('program =', user.program_selected)
  all_sites = list(query)

  orders = models.Order.all().filter('order_sheet =', order_sheet)
  orders.filter('state != ', 'new')
  orders.filter('program =', user.program_selected)
  order_sites = [o.site for o in orders]
  sites_without_order = [s for s in all_sites if s not in order_sites]
  sites_without_order.sort(key=lambda s: s.number)
  staff = models.Staff.all().order('name')
  template_dict = {'sites': sites_without_order,
                   'num_sites_without_order': len(sites_without_order),
                   'num_sites': len(all_sites),
                   'staff': staff,
                   'user': user,
                   'order_sheet': order_sheet,
                   'EMAIL_LOG': common.EMAIL_LOG,
                   'EMAIL_LOG_LINK': common.EMAIL_LOG_LINK,
                   }
  return common.Respond(request, 'sites_without_order', template_dict)


def SitesWithoutOrderSendEmail(request, order_sheet_id):
  subject = request.POST['subject']
  cc = request.POST['cc']
  body = request.POST['body']
  logging.info(request.POST)
  order_sheet = models.OrderSheet.get_by_id(int(order_sheet_id))
  if order_sheet is None:
    return http.HttpResponseNotFound(
        'No order_sheet exists with that key (%r)' % order_sheet_id)
  captains_by_site = {}
  site_captains = request.POST.getlist('site_captain')
  for sc in site_captains:
    site_id, captain_id = str(sc).split(' ')
    if site_id not in captains_by_site:
      captains_by_site[site_id] = []
    captains_by_site[site_id].append(captain_id)
  staff_id = request.POST['staff']
  staff = models.Staff.get_by_id(int(staff_id))
  sender = str(staff.email)
  for site_id in captains_by_site:
    site = models.NewSite.get_by_id(int(site_id))
    if not site:
      logging.warn('no site found for ID %s, skipping email', site_id)
      continue
    captains = []
    for captain_id in captains_by_site[site_id]:
      captain = models.Captain.get_by_id(int(captain_id))
      if not captain:
        logging.warn('no captain found for ID %s, skipping email', captain_id)
        continue
      captains.append(captain)
    to = list(set([str(c.email) for c in captains]))
    template_dict = {
        'to': to,
        'sender': sender,
        'captains': captains,
        'site': site,
        'order_sheet': order_sheet,
        'body': body,
    }

    logging.info('sending mail re: %s to %s', subject, to)
    common.SendMail(to, sender, cc, subject, body,
                    'sites_without_order_email.html', template_dict)
  return http.HttpResponseRedirect(urlresolvers.reverse(StaffHome))

import re


def FixCity(request):
  for s in models.NewSite.all():
    m = re.match('(.+ [0-9-]+) (.*)', s.city_state_zip)
    if not m:
      logging.info('not fixing site number %s: %r', s.number, s.city_state_zip)
      continue
    s.city_state_zip = m.groups()[0]
    logging.info('fixing site number %s: %r', s.number, s.city_state_zip)
    s.put()
  return http.HttpResponseRedirect(urlresolvers.reverse(StaffHome))


def FixLastEditor(request):
  for s in models.Order.all():
    if not s.last_editor:  # doesn't work if auto_current_user=True
      s.last_editor = s.modified_by
      s.put()
      logging.info('fixed last_editor for order #%d', s.key().id())
  return http.HttpResponseRedirect(urlresolvers.reverse(StaffHome))


def AddStandardKitOrder(request, prefix):
  user, _ = common.GetUser()
  skos = models.OrderSheet.all().filter('code = ', 'SDK').get()
  if not skos:
    logging.warn('can not find SDK order sheet')
    return http.HttpResponse(
        urlresolvers.reverse(AddStandardKitOrder, args=[prefix]))
  i = skos.item_set.get()
  if not i:
    logging.warn('can not find item for SDK order sheet')
    return http.HttpResponse(
        urlresolvers.reverse(AddStandardKitOrder, args=[prefix]))

  for site in models.NewSite.all().filter('program =', user.program_selected):
    if not site.number.startswith(prefix):
      logging.info('skipping site %r because wrong prefix %r',
                   site.number, prefix)
      continue
    if site.order_set.filter('order_sheet = ', skos).count():
      logging.info('skipping site %r because has SDK order', site.number)
      continue
    sko = models.Order(site=site, order_sheet=skos, state='Received')
    sko.put()
    oi = models.OrderItem(order=sko, item=i, quantity_float=1)
    oi.put()
    logging.info('created SDK order for site %r', site.number)
    sko.UpdateSubTotal()
    sko.put()

  return http.HttpResponse(
      urlresolvers.reverse(AddStandardKitOrder, args=[prefix]))


def RecomputeSearchPrefixes(request):
  for s in models.NewSite.all():
    taskqueue.add(url=urlresolvers.reverse(views.SitePut,
                                           args=[s.key().id()]))
  for c in models.Captain.all():
    taskqueue.add(url=urlresolvers.reverse(views.CaptainPut,
                                           args=[c.key().id()]))
  return http.HttpResponseRedirect(urlresolvers.reverse(StaffHome))


def RecomputeOrderLogistics(request):
  for c in models.Order.all():
    taskqueue.add(url=urlresolvers.reverse(order.OrderUpdateLogistics,
                                           args=[c.key().id()]))
  return http.HttpResponseRedirect(urlresolvers.reverse(StaffHome))


def RecomputeOrders(request):
  for o in models.Order.all():
    deferred.defer(order.RecomputeOrderItems, o)
  return http.HttpResponseRedirect(urlresolvers.reverse(StaffHome))


def DeleteEmptyOrderItems(request):
  for o in models.Order.all().filter('state !=', 'new'):
    for oi in o.orderitem_set:
      if oi.IsEmpty():
        oi.delete()
  return http.HttpResponseRedirect(urlresolvers.reverse(StaffHome))


def PutSuppliers(request):
  for o in models.Supplier.all():
    o.put()
  return http.HttpResponseRedirect(urlresolvers.reverse(StaffHome))


def FixProgramFromNumber(request, site_number=None):
  if site_number is None:
    for site in models.NewSite.all():
      taskqueue.add(url=urlresolvers.reverse(FixProgramFromNumber,
                                             args=[site.number]))
    return http.HttpResponseRedirect(urlresolvers.reverse(StaffHome))
  site = models.NewSite.all().filter('number =', site_number).get()
  if site and site.number:
    program = site.ProgramFromNumber()
    if program and program != site.program:
      logging.info('fixing program from %s to %s for site %s',
                   site.program, program, site.number)
      site.program = program
      site.put()
      site.SaveTheChildren()
  return http.HttpResponse('OK')


