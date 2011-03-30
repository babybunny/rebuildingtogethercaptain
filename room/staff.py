"""Staff views"""

import csv
import datetime
import logging
import os
from google.appengine.api import images
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import taskqueue
from google.appengine.ext.db import djangoforms
from google.appengine.ext.webapp import template

import django
from django import http
from django import shortcuts
from django.core import urlresolvers 
import forms
import models
import response
import common
import order
import views

TEST_SITE_NUMBER = '11999ZZZ'


def FindHome(user, default='/'):
  """Return path of user's home page, or a default page."""
  if user and user.email():
    staff = models.Staff.all().filter('email = ', user.email()).get()
    if staff:
      staff.last_welcome = datetime.datetime.now()
      staff.put()
      return urlresolvers.reverse(StaffHome)
    
    captain = models.Captain.all().filter('email = ', user.email()).get()
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
  order_sheets = list(models.OrderSheet.all())
  order_sheets.sort(key=lambda x: x.name)
  d = {'order_sheets': order_sheets,
       'test_site_number': TEST_SITE_NUMBER,
       }
  return common.Respond(request, 'staff_home', d)


def SiteJump(request):
  user, _, _ = common.GetUser(request)
  d = {'user': user}
  number = request.GET['number']
  site = models.NewSite.all().filter('number = ', number).get()
  if site is None:
    return http.HttpResponseRedirect(
      urlresolvers.reverse(StaffHome))
  else:
    return http.HttpResponseRedirect(
      urlresolvers.reverse(views.SiteView, args=[site.key().id()]))
    

def Scoreboard(request):
  welcomes = models.Captain.all().filter(
    'last_welcome != ', None).order('-last_welcome').fetch(20)
  staff_welcomes = models.Staff.all().filter(
    'last_welcome != ', None).order('-last_welcome').fetch(10)
  num_captains = models.Captain.all().count()
  num_captains_active = models.Captain.all().filter(
    'last_welcome != ', None).count()
  num_captains_with_tshirt = models.Captain.all().filter(
    'tshirt_size != ', None).count()

  def GetUserActivity(user_cls):
      user_activity = []
      welcomes = user_cls.all().filter(
          'last_welcome != ', None).order('-last_welcome').fetch(20)
      for c in welcomes:
          u = users.User(c.email)
          equery = models.Order.all().filter('state IN ', 
                                             ('Received', 'submitted'))
          equery.filter('last_editor =', u)
          orders = filter(lambda i: 'ZZZ' not in i.site.number, list(equery))
          user_activity.append((c, len(orders)))
      return user_activity

  sites = [s for s in models.NewSite.all() if 'ZZZ' not in s.number]
  num_sites = len(sites)
  total_site_budget = sum(s.budget for s in sites if s.budget)

  activity = []
  activity_rows = [
    ('All Orders', models.Order.all(), 
     urlresolvers.reverse(order.OrderList)),
    ('Check Requests', models.CheckRequest.all(),
     urlresolvers.reverse(views.CheckRequestList)),
    ('Vendor Receipts', models.VendorReceipt.all(),
     urlresolvers.reverse(views.VendorReceiptList)),
    ('In-kind Donations', models.InKindDonation.all(),
     urlresolvers.reverse(views.InKindDonationList)),
    ]

  order_sheets = models.OrderSheet.all().order('name')
  order_sheets = [o for o in order_sheets if o.visibility != 'Staff Only']
  for os in order_sheets:
      activity_rows.append(
      ('Form: %s' % os.name, 
       models.Order.all().filter('order_sheet =', os),
       urlresolvers.reverse(order.OrderList, args=[os.key().id()])))
    

  for name, query, link in activity_rows:
    items = filter(lambda i: 'ZZZ' not in i.site.number, query)
    started = len(items)
    total = sum(i.Total() for i in items)
    sites = len(set(i.site.number for i in items))
    editors = len(set(i.last_editor for i in items))
    submitted_orders = [i for i in items 
                        if i.state in ('Received', 'submitted')]
    submitted = len(submitted_orders)
    now = datetime.datetime.now()
    one = datetime.timedelta(days=1)
    recent = len([s for s in submitted_orders if now - s.modified < one])
    abandoned = len([i for i in items if i.state == 'new'])
    activity.append(
      (name, link, 
       submitted, recent, total, sites, editors, started, abandoned))

  d = {'last_welcomes': welcomes,
       'last_staff_welcomes': staff_welcomes,
       'activity': activity,
       'captain_activity': GetUserActivity(models.Captain),
       'staff_activity': GetUserActivity(models.Staff),
       'num_sites': num_sites,
       'num_captains': num_captains,
       'num_captains_active': num_captains_active,
       'pct_captains_active': num_captains_active * 100.0 / num_captains,
       'num_captains_with_tshirt': num_captains_with_tshirt,
       'total_site_budget': total_site_budget,
       }
  return common.Respond(request, 'scoreboard', d)


def SitesWithoutOrder(request, order_sheet_id):
  order_sheet = models.OrderSheet.get_by_id(int(order_sheet_id))
  if order_sheet is None:
    return http.HttpResponseNotFound(
      'No order_sheet exists with that key (%r)' % order_sheet_id)
  all_sites = list(models.NewSite.all())
  orders = models.Order.all().filter('order_sheet =', order_sheet)
  orders.filter('state != ', 'new')
  order_sites = [o.site for o in orders]
  sites_without_order = [s for s in all_sites if s not in order_sites]
  sites_without_order.sort(key=lambda s: s.number)
  template_dict = {'sites': sites_without_order,
                   'num_sites_without_order': len(sites_without_order),
                   'num_sites': len(all_sites),
                   'order_sheet': order_sheet,
                   'EMAIL_SENDER': common.EMAIL_SENDER,
                   'EMAIL_SENDER_READABLE': common.EMAIL_SENDER_READABLE,
                   'EMAIL_LOG': common.EMAIL_LOG,
                   }
  return common.Respond(request, 'sites_without_order', template_dict)
    

def SitesWithoutOrderSendEmail(request, order_sheet_id):
  subject = request.POST['subject']
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
      'captains': captains,
      'site': site,
      'order_sheet': order_sheet,
      'body': body,
      }
    
    logging.info('sending mail re: %s to %s', subject, to)
    common.SendMail(to, subject, body,
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
  for site in models.NewSite.all():
    if not site.number.startswith(prefix):
      logging.info('skipping site %r because wrong prefix %r', 
                   site.number, prefix)
      continue
    if site.order_set.filter('order_sheet = ', skos).count():
      logging.info('skipping site %r because has SDK order', site.number)      
      continue
    sko = models.Order(site=site, order_sheet=skos, state='Received')
    sko.put()
    oi = models.OrderItem(order=sko, item=i, quantity=1)
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

