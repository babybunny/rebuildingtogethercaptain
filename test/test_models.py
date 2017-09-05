"""Static models for use in testing.

The idea is to use this module (via remote_api_shell.py or a test URL handler)
to create a known set of models in a throwaway namespace for integration testing.

Also, these models may be used in unit tests.
"""

import datetime
import logging
import unittest2
from room import ndb_models


def CreateAll():
  """Creates all the models in this module.

  Returns: a dict of key name strings to ndb.Model instances. 
  """
  KEYS = dict()
  KEYS['STAFFPOSITION'] = ndb_models.StaffPosition(
    position_name="position one",
    hourly_rate=19.19,
    mileage_rate_after_date=["2016-01-01 0.54"],
  ).put()
  KEYS['STAFFPOSITION2'] = ndb_models.StaffPosition(
    position_name="position two",
    hourly_rate=19.19,
    mileage_rate_after_date=["2016-01-05 0.54"],
  ).put()
  KEYS['STAFFPOSITION3'] = ndb_models.StaffPosition(
    position_name="position three",
    hourly_rate_after_date=["2016-01-01 10.00", "2017-01-10 20.00"],
    mileage_rate_after_date=["2016-01-01 0.54", "2017-01-10 0.58"],
  ).put()

  KEYS['STAFF'] = ndb_models.Staff(
    name="Mister Staff",
    email="rebuildingtogether.staff@gmail.com",
    last_welcome=datetime.datetime(2017, 1, 30, 1, 2, 3),
    program_selected="2011 Test",
  ).put()
  KEYS['STAFF2'] = ndb_models.Staff(
    name="Mister Staff",
    email="rebuildingtogether.staff2@gmail.com",
  ).put()
  
  KEYS['CAPTAIN'] = ndb_models.Captain(
    name="Miss Captain",
    email="rebuildingtogether.capn@gmail.com",
    rooms_id="R00001",
    phone_mobile="222-333-4444",
    tshirt_size="Large",
    notes="You may say I'm a dreamer",
    last_welcome=datetime.datetime(2017, 1, 30, 1, 2, 3)
  ).put()

  KEYS['PROGRAM'] = ndb_models.Program(
    year=2011,
    name="TEST",
    site_number_prefix="110",
    status="Active"
  ).put()
  KEYS['PROGRAM2'] = ndb_models.Program(
    year=2012,
    name="TEST",
    site_number_prefix="120",
    status="Active"
  ).put()
  
  KEYS['JURISDICTION'] = ndb_models.Jurisdiction(
    name="FunkyTown"
  ).put()
  KEYS['JURISDICTION2'] = ndb_models.Jurisdiction(
    name="Unicorn Town"
  ).put()
  
  KEYS['SUPPLIER'] = ndb_models.Supplier(
    name='House of Supply',
    email='supplier@example.com',
    address='123 Supplier St, Main City, CA 99999',
    phone1='650 555 1111',
    phone2='650 555 2222',
    notes="""Supplier notes value""",
  ).put()

  KEYS['SITE'] = ndb_models.NewSite(
    jurisdiction_choice=KEYS['JURISDICTION'],
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
    # no street_number
    city_state_zip='Acorn City, CA, 99999',
    budget=5000,
    announcement_subject='announcement value',
    volunteer_signup_link='volunteer signup link value',
  ).put()

  KEYS['SITE2'] = ndb_models.NewSite(
    jurisdiction_choice=KEYS['JURISDICTION'],
    number='120TEST',
    program='2010 NRD',
    name='Fixyou Center',
    applicant='Mister Applicant, Sr.',
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
    budget=0,
    announcement_subject='announcement value',
    volunteer_signup_link='volunteer signup link value',
  ).put()

  KEYS['SITE3'] = ndb_models.NewSite(
    jurisdiction_choice=KEYS['JURISDICTION2'],
    number='111TEST',
    program='2011 Test',
    name='Rainbows',
    applicant='Jordy Carolina',
    applicant_home_phone='650 1357205',
    applicant_work_phone='650 555 8888',
    # None applicant_mobile_phone='650 555 7777',
    applicant_email='applicant@example.com',
    rating='rating value',
    roof='roof value',
    rrp_test='rrp test value',
    rrp_level='rrp level value',
    scope_of_work="""This is a big job. There is a lot to do.""",
    # None sponsor='Generous Group',
    street_number='123 Main Street',
    city_state_zip='Acorn City, CA, 99999',
    budget=0,
    announcement_subject='announcement value',
    volunteer_signup_link='volunteer signup link value',
  ).put()

  KEYS['SITECAPTAIN'] = ndb_models.SiteCaptain(
    site=KEYS['SITE'],
    captain=KEYS['CAPTAIN'],
    type='Construction'
  ).put()

  KEYS['STAFFTIME'] = ndb_models.StaffTime(  
    site=KEYS['SITE'],
    captain=KEYS['CAPTAIN'],
    position=KEYS['STAFFPOSITION'],
    program='2011 Test',
    state='submitted',
    hours=1.5,
    miles=11.1,
    activity_date=datetime.datetime(2017, 1, 30, 1, 2, 3),
    description="""Description of the time that staff spent."""
  ).put()

  KEYS['CHECKREQUEST'] = ndb_models.CheckRequest(
    site=KEYS['SITE'],
    captain=KEYS['CAPTAIN'],
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

  KEYS['CHECKREQUEST2'] = ndb_models.CheckRequest(
    site=KEYS['SITE'],
    state='new',
  ).put()

  KEYS['VENDORRECEIPT'] = ndb_models.VendorReceipt(
    site=KEYS['SITE'],
    captain=KEYS['CAPTAIN'],
    program='2011 Test',
    purchase_date=datetime.date(2011, 2, 3),
    amount=45.67,
    supplier=KEYS['SUPPLIER'],
    description='''For a receipt''',
    state='submitted',
  ).put()

  KEYS['INKINDDONATION'] = ndb_models.InKindDonation(
    site=KEYS['SITE'],
    captain=KEYS['CAPTAIN'],
    program='2011 Test',
    donation_date=datetime.date(2011, 2, 3),
    donor='Miss Donor',
    donor_phone='555-1212',
    donor_info='''A very nice donor, indeed''',
    labor_amount=45.67,
    materials_amount=23.45,
    description='''A very nice donation of labor and materials''',
    state='submitted',
  ).put()

  KEYS['ORDERSHEET'] = ndb_models.OrderSheet(
    default_supplier=KEYS['SUPPLIER'],
    name='Some Supplies',
    code='SOM',
    instructions='instructions value',
    logistics_instructions="""Pick these up somewhere nice.""",
    delivery_options='Yes',
  ).put()
  KEYS['ORDERSHEET2'] = ndb_models.OrderSheet(
    # no default_supplier
    name='Some More Supplies',
    code='SMS',
    instructions='instructions value',
    logistics_instructions="""Pick these up somewhere nice.""",
    delivery_options='Yes',
  ).put()
  KEYS['ORDERSHEET3'] = ndb_models.OrderSheet(
    # no default_supplier
    name='Debris Box',
    code='DEB',
    instructions='Put trash in it. Do not climb on or around.',
    logistics_instructions="""Put it on the curb.""",
    delivery_options='Yes',
    retrieval_options='Yes',
    pickup_options='No',
    visibility='Everyone'
  ).put()
  KEYS['ORDERSHEET4'] = ndb_models.OrderSheet(
    # no default_supplier
    name='VOID',
    code='VOI',
    instructions='This should be visible to Staff only',
    delivery_options='No',
    retrieval_options='No',
    pickup_options='No',
    visibility='Staff Only'
  ).put()

  KEYS['ITEM'] = ndb_models.Item(
    bar_code_number=1234,
    name='My First Item',
    appears_on_order_form=KEYS['ORDERSHEET'],
    order_form_section='The First Section',
    description="""A Very nice item, very nice.""",
    measure='Each',
    unit_cost=9.99,
    supplier=KEYS['SUPPLIER'],
    supplier_part_number='part1234',
    url='http://example.com/item',
    supports_extra_name_on_order=False,
  ).put()

  KEYS['ITEM2'] = ndb_models.Item(
    bar_code_number=1234,
    name='My Second Item',
    appears_on_order_form=KEYS['ORDERSHEET'],
    order_form_section='The Second Section',
    description="""A delicious item.""",
    measure='Box',
    unit_cost=4.99,
    supplier=KEYS['SUPPLIER'],
    supplier_part_number='part1244',
    url='http://example.com/item2',
    supports_extra_name_on_order=True,
  ).put()

  KEYS['ITEM3'] = ndb_models.Item(
    bar_code_number=1255,
    name='My Third Item',
    appears_on_order_form=KEYS['ORDERSHEET'],
    order_form_section='The Second Section',
    description="""A magnificent item.""",
    measure='Roll',
    unit_cost=3.99,
    supplier=KEYS['SUPPLIER'],
    supplier_part_number='part1233',
    url='http://example.com/item3',
    supports_extra_name_on_order=False,
  ).put()

  KEYS['ITEM4'] = ndb_models.Item(
    bar_code_number=1256,
    name='My Fourth Item',
    appears_on_order_form=KEYS['ORDERSHEET'],
    order_form_section='The Second Section',
    description="""An item with no unit cost!.""",
    measure='Roll',
    # None unit_cost=3.99,
    supplier=KEYS['SUPPLIER'],
    supplier_part_number='part1235',
    # None url='http://example.com/item4',
    supports_extra_name_on_order=False,
  ).put()

  KEYS['ITEM5'] = ndb_models.Item(
    bar_code_number=1256,
    name='Some More Item',
    appears_on_order_form=KEYS['ORDERSHEET2'],
    order_form_section='A Section',
    description="""The description is very short. Here it is.  But you can add an extra name.""",
    measure='Roll',
    unit_cost=99.99,
    supplier=KEYS['SUPPLIER'],
    # None url='http://example.com/item4',
    supports_extra_name_on_order=True,
  ).put()
  KEYS['ITEM6'] = ndb_models.Item(
    name='A deleted Item',
    appears_on_order_form=KEYS['ORDERSHEET4'],
    description="""This item has been discontinued.""",
    measure='Roll',
    unit_cost=12.34,
    supplier=KEYS['SUPPLIER'],
  ).put()

  KEYS['INVENTORYITEM'] = ndb_models.InventoryItem(
    item=KEYS['ITEM'],
    quantity=0,
    quantity_float=0.0,
    location='Everybody knows, its nowhere',
    available_on=datetime.date(2011, 3, 4)
  ).put()

  KEYS['ORDER'] = ndb_models.Order(
    site=KEYS['SITE'],
    order_sheet=KEYS['ORDERSHEET'],
    program='2011 Test',
    sub_total=9.99,
    notes='''These are very very nice order notes.''',
    state='Submitted',
    reconciliation_notes='''These are the reconciliation notes from the very nice staff''',
    invoice_date=datetime.datetime(2011, 4, 5, 1, 2, 3),
    vendor=KEYS['SUPPLIER'],
    logistics_start='a logistic start',
    logistics_end='a logistic end',
    logistics_instructions='''a logistic instruction'''
  ).put()

  KEYS['ORDER2'] = ndb_models.Order(
    site=KEYS['SITE'],
    order_sheet=KEYS['ORDERSHEET'],
    program='2011 Test',
    sub_total=8.00,  # a BS number
    notes='''These are very very nice order2 notes.''',
    state='new',
    actual_total=9.10,
    reconciliation_notes='''These are the reconciliation notes from the very nice staff on order2''',
    invoice_date=datetime.datetime(2011, 4, 5, 1, 2, 6),
    vendor=KEYS['SUPPLIER'],
    logistics_start='a logistic start',
    logistics_end='a logistic end',
    logistics_instructions='''another logistic instruction'''
  ).put()

  KEYS['DELIVERY'] = ndb_models.Delivery(
    site=KEYS['SITE'],
    delivery_date='Apr 12',
    contact='Joe Delivery',
    notes='''meet me at the side door''',
  ).put()

  KEYS['ORDERDELIVERY'] = ndb_models.OrderDelivery(
    order=KEYS['ORDER'],
    delivery=KEYS['DELIVERY'],
  ).put()

  KEYS['PICKUP'] = ndb_models.Pickup(
    site=KEYS['SITE'],
    pickup_date='Apr 13',
    return_date='Apr 19',
    contact='Joe Pickup',
    notes='''meet me at the side door for pickup''',
  ).put()

  KEYS['ORDERPICKUP'] = ndb_models.OrderPickup(
    order=KEYS['ORDER'],
    pickup=KEYS['PICKUP'],
  ).put()

  KEYS['RETRIEVAL'] = ndb_models.Retrieval(
    site=KEYS['SITE'],
    dropoff_date='Apr 14',
    retrieval_date='Apr 21',
    contact='Joe Retrieval',
    contact_phone='555-1212b',
    notes='''meet me at the side door for retrieval''',
  ).put()

  KEYS['ORDERRETRIEVAL'] = ndb_models.OrderRetrieval(
    order=KEYS['ORDER'],
    retrieval=KEYS['RETRIEVAL'],
  ).put()

  KEYS['ORDERITEM'] = ndb_models.OrderItem(
    order=KEYS['ORDER'],
    item=KEYS['ITEM'],
    supplier=KEYS['SUPPLIER'],
    quantity_float=1.1,
  ).put()

  KEYS['ORDERITEM2'] = ndb_models.OrderItem(
    order=KEYS['ORDER'],
    item=KEYS['ITEM2'],
    supplier=KEYS['SUPPLIER'],
    quantity_float=2.0,
    name='extra name',
  ).put()
  
  KEYS['ORDERITEM4'] = ndb_models.OrderItem(
    order=KEYS['ORDER'],
    item=KEYS['ITEM4'],
    supplier=KEYS['SUPPLIER'],
    quantity_float=1.0,
  ).put()

  """template
  KEYS['ORDER'] = ndb_models.Order(

  ).put()
  """

  logging.info('added keys: {}', KEYS.keys())
  return KEYS
  
  
def DeleteAll(KEYS):
  while KEYS:
    name, key = KEYS.popitem()
    logging.info('deleting {}', name)
    key.delete()


class ModelsTest(unittest2.TestCase):
  def testCreate(self):
    KEYS = CreateAll()
    self.assertTrue(KEYS)
    self.assertIn('ORDERITEM', KEYS)
    DeleteAll(KEYS)
    self.assertFalse(KEYS)
