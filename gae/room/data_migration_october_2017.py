

"""
ref: https://cloud.google.com/appengine/articles/update_schema
"""

import logging

import webapp2
from google.appengine.ext import ndb
from google.appengine.ext import deferred

from gae.room import ndb_models


site_number_to_program_map = {}


class DataMigrationOctober2017(webapp2.RequestHandler):

  BATCH_SIZE = 100

  def post(self):
    deferred.defer(self.update())
    self.response.write("""
        Schema update started. Check the console for task progress.
        <a href="/">View entities</a>.
        """)

  # exposed for testing
  def update(self):
    raise NotImplementedError("TBD: WIP")
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
    new_site_query = ndb_models.NewSite.query()
    new_sites, next_cursor, more = new_site_query.fetch_page(DataMigrationOctober2017.BATCH_SIZE, start_cursor=cursor)
    for new_site in new_sites:  # type: ndb_models.NewSite
      # from ndb_models.NewSite.ProgramFromNumber
      site_number = new_site.number
      two_digit_year = site_number[:2]
      assert two_digit_year.isdigit()
      year = int('20' + two_digit_year)
      deprecated_code = site_number[2]
      site_number_prefix = two_digit_year + deprecated_code
      if deprecated_code == '0':
        name = 'NRD'
      elif deprecated_code == '1':
        name = 'NRD'
      elif deprecated_code == '3':
        name = 'Misc'
      elif deprecated_code in '5':
        name = 'Safe'
      elif deprecated_code == '6':
        name = 'Safe'
      elif deprecated_code == '7':
        name = 'Energy'
      elif deprecated_code == '8':
        name = 'Teambuild'
      elif deprecated_code == '9':
        name = 'Youth'
      elif deprecated_code == 'Z':
        name = 'Test'
      else:
        raise Exception("Unexpected Site Number: {0}".format(site_number))
      program_type, _ = ndb_models.ProgramType.get_or_create(name=name)
      program, _ = ndb_models.Program.get_or_create(program_type_key=program_type, year=year, deprecated_code=deprecated_code)
      new_site.program_key = program.key
    self._complete(to_put, num_updated, more, self._update_site_task, next_cursor)

  def _update_model_task(self, model, cursor=None, num_updated=0):
    query = model.query()
    results, next_cursor, more = query.fetch_page(DataMigrationOctober2017.BATCH_SIZE, start_cursor=cursor)
    to_put = []
    for result in results:
      order.program = self._site_number_to_program_map[order.site]
      to_put.append(order)
    self._complete(to_put, num_updated, more, self._update_order_task, next_cursor)

  def _update_order_task(self, cursor=None, num_updated=0):
    reload(ndb_models)
    order_query = ndb_models.Order.query()
    orders, next_cursor, more = order_query.fetch_page(DataMigrationOctober2017.BATCH_SIZE, start_cursor=cursor)
    to_put = []
    for order in orders:
      assert order.program is None
      order.program = self._site_number_to_program_map[order.site]
      to_put.append(order)
    self._complete(to_put, num_updated, more, self._update_order_task, next_cursor)

  def _update_check_request(self, cursor=None, num_updated=0):
    reload(ndb_models)
    check_request_query = ndb_models.CheckRequest.query()
    check_requests, next_cursor, more = check_request_query.fetch_page(DataMigrationOctober2017.BATCH_SIZE, start_cursor=cursor)
    to_put = []
    for check_request in check_requests:
      assert check_request.program is None
      check_request.program = self._site_number_to_program_map[check_request.site]
      to_put.append(check_request)
    self._complete(to_put, num_updated, more, self._update_check_request, next_cursor)

  def _update_vendor_receipt(self, cursor=None, num_updated=0):
    reload(ndb_models)
    vendor_receipt_query = ndb_models.VendorReceipt.query()
    vendor_receipts, next_cursor, more = vendor_receipt_query.fetch_page(DataMigrationOctober2017.BATCH_SIZE, start_cursor=cursor)
    to_put = []
    for vendor_receipt in vendor_receipts:
      assert vendor_receipt.program is None
      vendor_receipt.program = self._site_number_to_program_map[vendor_receipt.site]
      to_put.append(vendor_receipt)
    self._complete(to_put, num_updated, more, self._update_vendor_receipt, next_cursor)

  def _update_in_kind_donation(self, cursor=None, num_updated=0):
    reload(ndb_models)
    in_kind_donation_query = ndb_models.InKindDonation.query()
    in_kind_donations, next_cursor, more = in_kind_donation_query.fetch_page(DataMigrationOctober2017.BATCH_SIZE, start_cursor=cursor)
    to_put = []
    for in_kind_donation in in_kind_donations:
      assert in_kind_donation.program is None
      in_kind_donation.program = self._site_number_to_program_map[in_kind_donation.site]
      to_put.append(in_kind_donation)
    self._complete(to_put, num_updated, more, self._update_in_kind_donation, next_cursor)

  def _update_staff_time(self, cursor=None, num_updated=0):
    reload(ndb_models)
    staff_time_query = ndb_models.StaffTime.query()
    staff_times, next_cursor, more = staff_time_query.fetch_page(DataMigrationOctober2017.BATCH_SIZE, start_cursor=cursor)
    to_put = []
    for staff_time in staff_times:
      assert staff_time.program is None
      staff_time.program = self._site_number_to_program_map[staff_time.site]
      to_put.append(staff_time)
    self._complete(to_put, num_updated, more, self._update_staff_time, next_cursor)

  def _update_expense(self, cursor=None, num_updated=0):
    reload(ndb_models)
    expense_query = ndb_models.Expense.query()
    expenses, next_cursor, more = expense_query.fetch_page(DataMigrationOctober2017.BATCH_SIZE, start_cursor=cursor)
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