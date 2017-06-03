"""Static models for use in testing.

The idea is to use this module (via remote_api_shell.py or a test URL handler)
to create a known set of models in a throwaway namespace for integration testing.

Also, these models may be used in unit tests.
"""

import datetime
from room import ndb_models

_KEYS = list()


def CreateAll():
  """Creates all the models in this module."""
  STAFFPOSITION = ndb_models.StaffPosition(
    position_name="position one",
    hourly_rate=19.19
  )
  staffposition_key = STAFFPOSITION.put()
  _KEYS.append(staffposition_key)

  STAFF = ndb_models.Staff(
    name="Mister Staff",
    email="rebuildingtogether.staff@gmail.com"
  )
  staff_key = STAFF.put()
  _KEYS.append(staff_key)
  
  CAPTAIN = ndb_models.Captain(
    name="Miss Captain",
    email="rebuildingtogether.capn@gmail.com",
    rooms_id="R00001",
    phone_mobile="222-333-4444",
    tshirt_size="Large",
    notes="You may say I'm a dreamer",
    last_welcome=datetime.datetime(2017, 1, 30, 1, 2, 3)
  )
  captain_key = CAPTAIN.put()
  _KEYS.append(captain_key)

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
  _KEYS.append(PROGRAM.put())
  _KEYS.append(PROGRAM2.put())
  
  JURISDICTION = ndb_models.Jurisdiction(
    name="FunkyTown"
  )
  jurisdiction_key = JURISDICTION.put()
  _KEYS.append(jurisdiction_key)
  
  SUPPLIER = ndb_models.Supplier(
    name='House of Supply',
    email='supplier@example.com',
    address='123 Supplier St, Main City, CA 99999',
    phone1='650 555 1111',
    phone2='650 555 2222',
    notes="""Supplier notes value""",
  )
  supplier_key = SUPPLIER.put()
  _KEYS.append(supplier_key)

  ORDERSHEET = ndb_models.OrderSheet(
    default_supplier=supplier_key,
    name='Some Supplies',
    code='SOM',
    instructions='instructions value',
    logistics_instructions="""Pick these up somewhere nice.""",
    delivery_options='Yes',
  )
  _KEYS.append(ORDERSHEET.put())

  SITE = ndb_models.NewSite(
    jurisdiction_choice=jurisdiction_key,
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
  )
  site_key = SITE.put()
  _KEYS.append(site_key)

  STAFFTIME = ndb_models.StaffTime(  
    site=site_key,
    captain=captain_key,
    position=staffposition_key,
    program='2011 Test',
    state='submitted',
    hours=1.5,
    miles=11.1,
    activity_date=datetime.datetime(2017, 1, 30, 1, 2, 3),
    description="""Description of the time that staff spent."""
  )
  _KEYS.append(STAFFTIME.put())

  SITECAPTAIN = ndb_models.SiteCaptain(
    site=site_key,
    captain=captain_key,
    type='Construction'
  )
  _KEYS.append(SITECAPTAIN.put())

  
def DeleteAll():
  global _KEYS
  while _KEYS:
    _KEYS.pop().delete()
  _KEYS = list()


def main(argv):
  host_port = argv[1]
  
if __name__ == '__main__':
  main()
