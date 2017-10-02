"""Scoreboard views"""

import datetime
import logging

from google.appengine.api import users

import common
import order
import views


def AllProgramsScoreboard(request):
  site_programs = {}
  for site in models.NewSite.all():
    site_programs[site.program] = site_programs.get(site.program, 0) + 1
  logging.info(site_programs)
  programs = ((p, site_programs.get(p, 0)) for p in common.PROGRAMS)
  missing_programs = set(site_programs) - set(common.PROGRAMS)
  return common.Respond(request, 'all_programs_scoreboard', locals())


def Scoreboard(request):
  user, _, _ = common.GetUser(request)
  num_captains = models.Captain.all().count()
  num_captains_active = models.Captain.all().filter(
    'last_welcome != ', None).count()
  pct_captains_active = num_captains_active * 100.0 / num_captains
  num_captains_with_tshirt = models.Captain.all().filter(
    'tshirt_size != ', None).count()

  query = models.NewSite.all().order('number')
  query.filter('program =', user.program_selected)
  sites = list(query)
  num_sites = len(sites)
  total_site_budget = sum(s.budget for s in sites if s.budget)
  return common.Respond(request, 'scoreboard', locals())


def _ScoreboardUsers(user_cls, request):
  user, _, _ = common.GetUser(request)
  user_activity = []
  welcomes = user_cls.all().filter(
    'last_welcome != ', None).order('-last_welcome').fetch(20)
  for c in welcomes:
    u = users.User(c.email)
    equery = models.Order.all().filter('state IN ',
                                       ('Received', 'submitted',
                                        'Being Filled'))
    equery.filter('program =', user.program_selected)
    equery.filter('created_by =', u)
    orders = list(equery)
    recent_orders = filter(lambda o: o.created > c.last_welcome, orders)
    user_activity.append((c, len(orders), len(recent_orders)))
  return user_activity


def ScoreboardCaptains(request):
  return common.Respond(
    request, 'scoreboard_users',
    {'user_activity': _ScoreboardUsers(models.Captain, request),
     'name': 'Captain'})


def ScoreboardStaff(request):
  return common.Respond(
    request, 'scoreboard_users',
    {'user_activity': _ScoreboardUsers(models.Staff, request),
     'name': 'Staff'})


def ScoreboardOrders(request):
  user, _, _ = common.GetUser(request)
  activity = []
  activity_rows = [
    ('All Orders',
     models.Order.all().filter('program =', user.program_selected),
     urlresolvers.reverse(order.OrderList)),
    ('Check Requests',
     models.CheckRequest.all().filter('program =', user.program_selected),
     urlresolvers.reverse(views.CheckRequestList)),
    ('Vendor Receipts',
     models.VendorReceipt.all().filter('program =', user.program_selected),
     urlresolvers.reverse(views.VendorReceiptList)),
    ('In-kind Donations',
     models.InKindDonation.all().filter('program =', user.program_selected),
     urlresolvers.reverse(views.InKindDonationList)),
  ]
  order_sheets = models.OrderSheet.all().order('name')
  order_sheets = [o for o in order_sheets if o.visibility != 'Staff Only']
  for os in order_sheets:
    query = models.Order.all().filter('program =', user.program_selected)
    query.filter('order_sheet =', os)
    activity_rows.append(
      ('Form: %s' % os.name[0:20], query,
       urlresolvers.reverse(order.OrderList, args=[os.key().id()])))

  now = datetime.datetime.now()
  one = datetime.timedelta(days=1)

  for name, query, link in activity_rows:
    items = filter(lambda i: 'ZZZ' not in i.site.number, query)
    total = sum(i.Total() for i in items)
    sites = len(set(i.site.number for i in items))
    editors = len(set(i.last_editor for i in items))
    totals_by_state = {}
    for i in items:
      totals_by_state[i.state] = totals_by_state.get(i.state, 0) + 1
    received_orders = [i for i in items
                       if i.state in ('Received', 'submitted')]
    recent = len([s for s in received_orders if now - s.modified < one])
    logging.info('got activity row: %s', name)
    activity.append(
      (name, link,
       totals_by_state.get('Received', 0) +
       totals_by_state.get('submitted', 0),
       recent,
       total, sites, editors,
       totals_by_state.get('Deleted', 0) + totals_by_state.get('new', 0),
       totals_by_state.get('new', 0),
       totals_by_state.get('Being Filled', 0),
       totals_by_state.get('Reconciled', 0)))

  d = locals()
  return common.Respond(request, 'scoreboard_orders', d)
