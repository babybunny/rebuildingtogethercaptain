"""Static models for use in testing.

The idea is to use this module (via remote_api_shell.py or a test URL handler)
to create a known set of models in a throwaway namespace for integration testing.

Also, these models may be used in unit tests.
"""

import datetime
import logging
from room import ndb_models

_KEYS = dict()


def CreateAll():
  """Creates all the models in this module."""
  _KEYS['STAFFPOSITION'] = ndb_models.StaffPosition(
    position_name="position one",
    hourly_rate=19.19
  ).put()

  _KEYS['STAFF'] = ndb_models.Staff(
    name="Mister Staff",
    email="rebuildingtogether.staff@gmail.com"
  ).put()
  
  _KEYS['CAPTAIN'] = ndb_models.Captain(
    name="Miss Captain",
    email="rebuildingtogether.capn@gmail.com",
    rooms_id="R00001",
    phone_mobile="222-333-4444",
    tshirt_size="Large",
    notes="You may say I'm a dreamer",
    last_welcome=datetime.datetime(2017, 1, 30, 1, 2, 3)
  ).put()

  _KEYS['PROGRAM'] = ndb_models.Program(
    year=2011,
    name="TEST",
    site_number_prefix="110",
    status="Active"
  ).put()
  _KEYS['PROGRAM2'] = ndb_models.Program(
    year=2012,
    name="TEST",
    site_number_prefix="120",
    status="Active"
  ).put()
  
  _KEYS['JURISDICTION'] = ndb_models.Jurisdiction(
    name="FunkyTown"
  ).put()
  
  _KEYS['SITE'] = ndb_models.NewSite(
    jurisdiction_choice=_KEYS['JURISDICTION'],
    number='110TEST',
    program='2011 Test',
    name='Fixme Center',
    applicant='Mister Applicant',
    applicant_home_phone='650 555 9999',
    applicant_work_phone='650 555 8888',
    applicant_mobile_phone='650 555 7777',
    applicant_email='applicant@example.com',
    rating='rating value',
    roof='roof value',
    rrp_test='rrp test value',
    rrp_level='rrp level value',
    scope_of_work="""This is a big job. There is a lot to do.""",
    sponsor='Generous Group',
    street_number='123 Main Street',
    city_state_zip='Acorn City, CA, 99999',
    budget=5000,
    announcement_subject='announcement value',
    volunteer_signup_link='volunteer signup link value',
  ).put()

  _KEYS['SITECAPTAIN'] = ndb_models.SiteCaptain(
    site=_KEYS['SITE'],
    captain=_KEYS['CAPTAIN'],
    type='Construction'
  ).put()

  _KEYS['STAFFTIME'] = ndb_models.StaffTime(  
    site=_KEYS['SITE'],
    captain=_KEYS['CAPTAIN'],
    position=_KEYS['STAFFPOSITION'],
    program='2011 Test',
    state='submitted',
    hours=1.5,
    miles=11.1,
    activity_date=datetime.datetime(2017, 1, 30, 1, 2, 3),
    description="""Description of the time that staff spent."""
  ).put()

  _KEYS['CHECKREQUEST'] = ndb_models.CheckRequest(
    site=_KEYS['SITE'],
    captain=_KEYS['CAPTAIN'],
    program='2011 Test',
    payment_date=datetime.date(2011, 2, 3),
    labor_amount=45.67,
    materials_amount=23.45,
    food_amount=12.34,
    description='''For Services Rendered''',
    name='Mister Payable To',
    address='123 checkrequest street',
    tax_id='123-456-8790',
    form_of_business='Corporation',
    state='submitted',
  ).put()

  _KEYS['SUPPLIER'] = ndb_models.Supplier(
    name='House of Supply',
    email='supplier@example.com',
    address='123 Supplier St, Main City, CA 99999',
    phone1='650 555 1111',
    phone2='650 555 2222',
    notes="""Supplier notes value""",
  ).put()

  _KEYS['ORDERSHEET'] = ndb_models.OrderSheet(
    default_supplier=_KEYS['SUPPLIER'],
    name='Some Supplies',
    code='SOM',
    instructions='instructions value',
    logistics_instructions="""Pick these up somewhere nice.""",
    delivery_options='Yes',
  ).put()


  logging.info('added keys: {}', _KEYS.keys())

  
def DeleteAll():
  global _KEYS
  while _KEYS:
    name, key = _KEYS.popitem()
    logging.info('deleting {}', name)
    key.delete()
  _KEYS = dict()
