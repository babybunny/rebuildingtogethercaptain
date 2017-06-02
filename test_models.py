"""Static models for use in testing.

The idea is to use this module (via remote_api_shell.py or a test URL handler)
to create a known set of models in a throwaway namespace for integration testing.

Also, these models may be used in unit tests.
"""

import datetime
from room import ndb_models

STAFFPOSITION = ndb_models.StaffPosition(
  position_name="position one",
  hourly_rate=19.19
  )

STAFF = ndb_models.Staff(
  name="Mister Staff",
  email="rebuildingtogether.staff@gmail.com"
  )

CAPTAIN = ndb_models.Captain(
  name="Miss Captain",
  email="rebuildingtogether.capn@gmail.com",
  rooms_id="R00001",
  phone_mobile="222-333-4444",
  tshirt_size="Large",
  notes="You may say I'm a dreamer",
  last_welcome=datetime.datetime(2017, 1, 30, 1, 2, 3)
  )

PROGRAM = ndb_models.Program(
  year=2011,
  name="TEST",
  site_number_prefix="110",
  status="Active"
  )
PROGRAM2 = ndb_models.Program(
  year=2012,
  name="TEST",
  site_number_prefix="120",
  status="Active"
  )

JURISDICTION = ndb_models.Jurisdiction(
  name="FunkyTown"
  )

SUPPLIER = ndb_models.Supplier(
  name='House of Supply',
  email='supplier@example.com',
  address='123 Supplier St, Main City, CA 99999',
  phone1='650 555 1111',
  phone2='650 555 2222',
  notes="""Supplier notes value""",
  )

ORDERSHEET = ndb_models.OrderSheet(
  name='Some Supplies',
  code='SOM',
  instructions='instructions value',
  logistics_instructions="""Pick these up somewhere nice.""",
  # Set below default_supplier=ndb.KeyProperty(kind=Supplier),
  delivery_options='Yes',
)

SITE = ndb_models.Site(
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
  # UNUSED? jurisdiction=ndb.StringProperty() ,
  # Set below jurisdiction_choice=ndb.KeyProperty(kind=Jurisdiction),
  scope_of_work="""This is a big job. There is a lot to do.""",
  sponsor='Generous Group',
  street_number='123 Main Street',
  city_state_zip='Acorn City, CA, 99999',
  budget=5000,
  announcement_subject='announcement value',
  volunteer_signup_link='volunteer signup link value',
  )

SITECAPTAIN = ndb_models.SiteCaptain(
  type='Construction'
  )

_KEYS = list()


def CreateAll():
  """Creates all the models in this module."""
  _KEYS.append(STAFFPOSITION.put())
  _KEYS.append(STAFF.put())

  captain_key = CAPTAIN.put()
  _KEYS.append(captain_key)

  _KEYS.append(PROGRAM.put())
  _KEYS.append(PROGRAM2.put())
  jurisdiction_key = JURISDICTION.put()
  _KEYS.append(jurisdiction_key)

  supplier_key = SUPPLIER.put()  
  _KEYS.append(supplier_key)

  ORDERSHEET.supplier = supplier_key
  _KEYS.append(ORDERSHEET.put())

  SITE.jurisdiction_choice = jurisdiction_key
  site_key = SITE.put()
  _KEYS.append(site_key)

  SITECAPTAIN.site = site_key
  SITECAPTAIN.captain = captain_key
  _KEYS.append(SITECAPTAIN.put())
  
def DeleteAll():
  global _KEYS
  for k in _KEYS:
    k.delete()
  _KEYS = list()

