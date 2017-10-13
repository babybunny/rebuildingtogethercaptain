"""
ref: https://cloud.google.com/appengine/articles/update_schema
"""

import logging

import webapp2
from google.appengine.ext import ndb
from google.appengine.ext import deferred

from gae.room import models_v2
from gae.room import models_v1


site_number_to_program_map = {}


class October2017Migration(webapp2.RequestHandler):

  BATCH_SIZE = 100

  def post(self):
    deferred.defer(self.update())
    self.response.write("""
        Schema update started. Check the console for task progress.
        <a href="/">View entities</a>.
        """)

  # exposed for testing
  def update(self):
    self._site_number_to_program_map = {}
    self._update_site_task()
    self._update_staff_task()
    self._update_order_task()
    self._update_check_request()
    self._update_vendor_receipt()
    self._update_staff_time()
    self._update_in_kind_donation()
    self._update_expense()

  def _update_site_task(self, cursor=None, num_updated=0):
    to_put = []
    new_site_query = models_v1.NewSite.query()
    new_sites, next_cursor, more = new_site_query.fetch_page(October2017Migration.BATCH_SIZE, start_cursor=cursor)
    for new_site in new_sites:
      # from models_v1.NewSite.ProgramFromNumber
      site_number = new_site.number
      two_digit_year = site_number[:2]
      assert two_digit_year.isdigit()
      year = int('20' + two_digit_year)
      mode = site_number[2]
      site_number_prefix = two_digit_year + mode
      if mode == '0':
        name = 'NRD'
      elif mode == '1':
        name = 'NRD'
      elif mode == '3':
        name = 'Misc'
      elif mode in '5':
        name = 'Safe'
      elif mode == '6':
        name = 'Safe'
      elif mode == '7':
        name = 'Energy'
      elif mode == '8':
        name = 'Teambuild'
      elif mode == '9':
        name = 'Youth'
      elif mode == 'Z':
        name = 'Test'
      else:
        raise Exception("Unexpected Site Number: {0}".format(site_number))
      program_query = models_v2.Program.query()
      program_query = program_query.filter(models_v2.Program.year == year)
      program_query = program_query.filter(models_v2.Program.name == name)
      program_query = program_query.filter(models_v2.Program.site_number_prefix == site_number_prefix)
      program = program_query.get()
      if not program:
        program = models_v2.Program(year=year, name=name, site_number_prefix=site_number_prefix)
        program.put()
      site = models_v2.Site()

      site.number = new_site.number
      site.program = program.key
      site.name = new_site.name
      site.applicant = new_site.applicant
      site.applicant_home_phone = new_site.applicant_home_phone
      site.applicant_work_phone = new_site.applicant_work_phone
      site.applicant_mobile_phone = new_site.applicant_mobile_phone
      site.applicant_email = new_site.applicant_email
      site.rating = new_site.rating
      site.roof = new_site.roof
      site.rrp_test = new_site.rrp_test
      site.rrp_level = new_site.rrp_level
      site.jurisdiction = new_site.jurisdiction
      site.jurisdiction_choice = new_site.jurisdiction_choice
      site.scope_of_work = new_site.scope_of_work
      site.sponsor = new_site.sponsor
      site.street_number = new_site.street_number
      site.city_state_zip = new_site.city_state_zip
      site.budget = new_site.budget
      site.announcement_subject = new_site.announcement_subject
      site.announcement_body = new_site.announcement_body
      site.search_prefixes = new_site.search_prefixes
      site.photo_link = new_site.photo_link
      site.volunteer_signup_link = new_site.volunteer_signup_link
      site.latest_computed_expenses = new_site.latest_computed_expenses
      to_put.append(site)
      self._site_number_to_program_map[site.key] = program.key
    self._complete(to_put, num_updated, more, self._update_site_task, next_cursor)

  def _update_staff_task(self, cursor=None, num_updated=0):
    pass  # program_selected will be None which is fine, nothing to do here

  def _update_order_task(self, cursor=None, num_updated=0):
    reload(models_v2)
    order_query = models_v2.Order.query()
    orders, next_cursor, more = order_query.fetch_page(October2017Migration.BATCH_SIZE, start_cursor=cursor)
    to_put = []
    for order in orders:
      assert order.program is None
      order.program = self._site_number_to_program_map[order.site]
      to_put.append(order)
    self._complete(to_put, num_updated, more, self._update_order_task, next_cursor)

  def _update_check_request(self, cursor=None, num_updated=0):
    reload(models_v2)
    check_request_query = models_v2.CheckRequest.query()
    check_requests, next_cursor, more = check_request_query.fetch_page(October2017Migration.BATCH_SIZE, start_cursor=cursor)
    to_put = []
    for check_request in check_requests:
      assert check_request.program is None
      check_request.program = self._site_number_to_program_map[check_request.site]
      to_put.append(check_request)
    self._complete(to_put, num_updated, more, self._update_check_request, next_cursor)

  def _update_vendor_receipt(self, cursor=None, num_updated=0):
    reload(models_v2)
    vendor_receipt_query = models_v2.VendorReceipt.query()
    vendor_receipts, next_cursor, more = vendor_receipt_query.fetch_page(October2017Migration.BATCH_SIZE, start_cursor=cursor)
    to_put = []
    for vendor_receipt in vendor_receipts:
      assert vendor_receipt.program is None
      vendor_receipt.program = self._site_number_to_program_map[vendor_receipt.site]
      to_put.append(vendor_receipt)
    self._complete(to_put, num_updated, more, self._update_vendor_receipt, next_cursor)

  def _update_in_kind_donation(self, cursor=None, num_updated=0):
    reload(models_v2)
    in_kind_donation_query = models_v2.InKindDonation.query()
    in_kind_donations, next_cursor, more = in_kind_donation_query.fetch_page(October2017Migration.BATCH_SIZE, start_cursor=cursor)
    to_put = []
    for in_kind_donation in in_kind_donations:
      assert in_kind_donation.program is None
      in_kind_donation.program = self._site_number_to_program_map[in_kind_donation.site]
      to_put.append(in_kind_donation)
    self._complete(to_put, num_updated, more, self._update_in_kind_donation, next_cursor)

  def _update_staff_time(self, cursor=None, num_updated=0):
    reload(models_v2)
    staff_time_query = models_v2.StaffTime.query()
    staff_times, next_cursor, more = staff_time_query.fetch_page(October2017Migration.BATCH_SIZE, start_cursor=cursor)
    to_put = []
    for staff_time in staff_times:
      assert staff_time.program is None
      staff_time.program = self._site_number_to_program_map[staff_time.site]
      to_put.append(staff_time)
    self._complete(to_put, num_updated, more, self._update_staff_time, next_cursor)

  def _update_expense(self, cursor=None, num_updated=0):
    reload(models_v2)
    expense_query = models_v2.Expense.query()
    expenses, next_cursor, more = expense_query.fetch_page(October2017Migration.BATCH_SIZE, start_cursor=cursor)
    to_put = []
    for expense in expenses:
      assert expense.program is None
      expense.program = self._site_number_to_program_map[expense.site]
      to_put.append(expense)
    self._complete(to_put, num_updated, more, self._update_expense, next_cursor)

  def _complete(self, to_put, num_updated, more, callback, next_cursor):
    num_updated += len(to_put)
    to_put and ndb.put_multi(to_put)
    logging.info("Updated {} ...".format(num_updated))
    more and deferred.defer(callback, cursor=next_cursor, num_updated=num_updated)
