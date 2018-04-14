"""Protorpc messages and conversion functions that can be used in multiple APIs..

This is the place to put messages that are one-to-one with datastore Kinds
(classes in ndb_models.py) and conversion functions. By convention, the conversions are
  message_instance = KindModelToMessage(model_instance)
  KindMessageToModel(message_instance, model_instance)

Messages and utility functions that are specific to a particular API module should be defined in that module. This is shared code.
"""

import datetime

from google.appengine.ext import ndb
from protorpc import messages
from protorpc import remote

import ndb_models


class SimpleId(messages.Message):
  id = messages.IntegerField(1, required=True)


################
# Jurisdiction #
################

def JurisdictionModelToMessage(mdl):
  s = Jurisdiction(
    name=mdl.name,
    id=mdl.key.integer_id(),
  )
  return s


def JurisdictionMessageToModel(msg, mdl):
  mdl.name = msg.name
  return mdl


class Jurisdiction(messages.Message):
  id = messages.IntegerField(1)
  name = messages.StringField(2)


#########
# Staff #
#########

def StaffModelToMessage(mdl):
  s = Staff(
    name=mdl.name,
    email=mdl.email,
    program_selected=mdl.program_selected,
    notes=mdl.notes,
    id=mdl.key.integer_id(),
  )
  if mdl.since:
    s.since = mdl.since.isoformat()  # datetime, for display only
  if mdl.last_welcome:
    s.last_welcome = mdl.last_welcome.isoformat()  # datetime, for display only
  return s


def StaffMessageToModel(msg, mdl):
  mdl.name = msg.name
  if msg.email:
    mdl.email = msg.email.lower()
  mdl.program_selected = msg.program_selected
  mdl.notes = msg.notes
  # can't set "since" or "last_welcome", they are automatic
  return mdl


class Staff(messages.Message):
  id = messages.IntegerField(1)
  name = messages.StringField(2)
  email = messages.StringField(3)
  last_welcome = messages.StringField(4)
  program_selected = messages.StringField(5)
  notes = messages.StringField(6)
  since = messages.StringField(7)


###########
# Captain #
###########

def CaptainModelToMessage(mdl):
  s = Captain(
    name=mdl.name,
    email=mdl.email,
    rooms_id=mdl.rooms_id,
    phone_mobile=mdl.phone_mobile,
    phone_work=mdl.phone_work,
    phone_home=mdl.phone_home,
    phone_fax=mdl.phone_fax,
    phone_other=mdl.phone_other,
    tshirt_size=mdl.tshirt_size,
    notes=mdl.notes,
    last_editor=unicode(mdl.last_editor),
    id=mdl.key.integer_id(),
  )
  if mdl.last_welcome:
    s.last_welcome = mdl.last_welcome.isoformat()  # datetime, fo
  if mdl.modified:
    s.modified = mdl.modified.isoformat()  # datetime, for display only
  return s


def CaptainMessageToModel(msg, mdl):
  mdl.name = msg.name
  if msg.email:
    mdl.email = msg.email.lower()
  mdl.rooms_id = msg.rooms_id
  mdl.phone_mobile = msg.phone_mobile
  mdl.phone_work = msg.phone_work
  mdl.phone_home = msg.phone_home
  mdl.phone_fax = msg.phone_fax
  mdl.phone_other = msg.phone_other
  mdl.tshirt_size = msg.tshirt_size
  mdl.notes = msg.notes
  # can't set automatic fields
  # last_welcome modified last_editor
  return mdl


class Captain(messages.Message):
  id = messages.IntegerField(1)
  name = messages.StringField(2)
  email = messages.StringField(3)
  rooms_id = messages.StringField(4)
  phone_mobile = messages.StringField(5)
  phone_work = messages.StringField(6)
  phone_home = messages.StringField(7)
  phone_fax = messages.StringField(8)
  phone_other = messages.StringField(9)
  tshirt_size = messages.StringField(10)
  notes = messages.StringField(11)
  last_welcome = messages.StringField(12)
  modified = messages.StringField(13)
  last_editor = messages.StringField(14)
  # search_prefixes is internal only


############
# Supplier #
############

def SupplierModelToMessage(mdl):
  s = Supplier(
    id=mdl.key.integer_id(),
    name=mdl.name,
    email=mdl.email,
    address=mdl.address,
    phone1=mdl.phone1,
    phone2=mdl.phone2,
    notes=mdl.notes,
    active=mdl.active,
    visibility=mdl.visibility,
  )
  if mdl.since:
    s.since = mdl.since.isoformat()  # datetime, for display only
  return s


def SupplierMessageToModel(msg, mdl):
  mdl.name = msg.name
  if msg.email:
    mdl.email = msg.email.lower()
  mdl.address = msg.address
  mdl.phone1 = msg.phone1
  mdl.phone2 = msg.phone2
  mdl.notes = msg.notes
  mdl.active = msg.active
  mdl.visibility = msg.visibility
  # can't set "since", it's automatic
  return mdl


class Supplier(messages.Message):
  name = messages.StringField(1)
  email = messages.StringField(2)
  address = messages.StringField(3)
  phone1 = messages.StringField(4)
  phone2 = messages.StringField(5)
  notes = messages.StringField(6)
  since = messages.StringField(7)
  active = messages.StringField(8)
  visibility = messages.StringField(9)
  id = messages.IntegerField(10)


############
# NewSite #
############

def NewSiteModelToMessage(mdl):
  s = NewSite(
    id=mdl.key.integer_id(),
    rating=mdl.rating,
    applicant=mdl.applicant,
    scope_of_work=mdl.scope_of_work,
    number=mdl.number,
    city_state_zip=mdl.city_state_zip,
    sponsor=mdl.sponsor,
    photo_link=mdl.photo_link,
    street_number=mdl.street_number,
    program=mdl.program,
    applicant_mobile_phone=mdl.applicant_mobile_phone,
    rrp_level=mdl.rrp_level,
    applicant_home_phone=mdl.applicant_home_phone,
    rrp_test=mdl.rrp_test,
    applicant_work_phone=mdl.applicant_work_phone,
    roof=mdl.roof,
    name=mdl.name,
    announcement_subject=mdl.announcement_subject,
    volunteer_signup_link=mdl.volunteer_signup_link,
    announcement_body=mdl.announcement_body,
    jurisdiction=mdl.jurisdiction,
    budget=mdl.budget,
    applicant_email=mdl.applicant_email,
  )
  # any special handling, like for user objects or datetimes
  # internal only: search_prefixes
  if mdl.jurisdiction_choice:
    s.jurisdiction_choice = mdl.jurisdiction_choice.integer_id()

  return s


def NewSiteMessageToModel(msg, mdl):
  mdl.rating = msg.rating
  mdl.applicant = msg.applicant
  mdl.scope_of_work = msg.scope_of_work
  mdl.number = msg.number
  mdl.city_state_zip = msg.city_state_zip
  mdl.sponsor = msg.sponsor
  mdl.photo_link = msg.photo_link
  mdl.street_number = msg.street_number
  mdl.program = msg.program
  mdl.applicant_mobile_phone = msg.applicant_mobile_phone
  mdl.rrp_level = msg.rrp_level
  mdl.applicant_home_phone = msg.applicant_home_phone
  mdl.rrp_test = msg.rrp_test
  mdl.applicant_work_phone = msg.applicant_work_phone
  mdl.roof = msg.roof
  mdl.name = msg.name
  mdl.announcement_subject = msg.announcement_subject
  mdl.volunteer_signup_link = msg.volunteer_signup_link
  mdl.announcement_body = msg.announcement_body
  mdl.budget = msg.budget
  mdl.applicant_email = msg.applicant_email
  # can't set automatic fields:
  # search_prefixes

  if msg.jurisdiction_choice:
    mdl.jurisdiction_choice = ndb.Key(ndb_models.Jurisdiction, msg.jurisdiction_choice)

  return mdl


class NewSite(messages.Message):
  id = messages.IntegerField(1)
  rating = messages.StringField(2)
  applicant = messages.StringField(3)
  scope_of_work = messages.StringField(4)
  number = messages.StringField(5)
  city_state_zip = messages.StringField(6)
  sponsor = messages.StringField(7)
  photo_link = messages.StringField(8)
  search_prefixes = messages.StringField(9)
  street_number = messages.StringField(10)
  program = messages.StringField(11)
  applicant_mobile_phone = messages.StringField(12)
  rrp_level = messages.StringField(13)
  applicant_home_phone = messages.StringField(14)
  rrp_test = messages.StringField(15)
  applicant_work_phone = messages.StringField(16)
  roof = messages.StringField(17)
  name = messages.StringField(18)
  announcement_subject = messages.StringField(19)
  volunteer_signup_link = messages.StringField(20)
  jurisdiction_choice = messages.IntegerField(21)
  announcement_body = messages.StringField(22)
  jurisdiction = messages.StringField(23)
  budget = messages.IntegerField(24)
  applicant_email = messages.StringField(25)


############
# Site #
############

def SiteModelToMessage(mdl):
  s = Site(
    id=mdl.key.integer_id(),
    number=mdl.number,
  )
  # Any special handling, like for user objects or datetimes
  return s


def SiteMessageToModel(msg, mdl):
  mdl.number = msg.number
  # can't set automatic fields:
  # TODO
  return mdl


class Site(messages.Message):
  id = messages.IntegerField(1)
  number = messages.StringField(2)


############
# OrderSheet #
############

def OrderSheetModelToMessage(mdl):
  s = OrderSheet(
    id=mdl.key.integer_id(),
    code=mdl.code,
    name=mdl.name,
    visibility=mdl.visibility,
    supports_internal_invoice=mdl.supports_internal_invoice,
    instructions=mdl.instructions,
    logistics_instructions=mdl.logistics_instructions,
    delivery_options=mdl.delivery_options,
    retrieval_options=mdl.retrieval_options,
    pickup_options=mdl.pickup_options,
    borrow_options=mdl.borrow_options,
  )
  # any special handling, like for user objects or datetimes
  if mdl.default_supplier:
    s.default_supplier = mdl.default_supplier.integer_id()
  return s


def OrderSheetMessageToModel(msg, mdl):
  mdl.code = msg.code
  mdl.name = msg.name
  mdl.visibility = msg.visibility
  mdl.supports_internal_invoice = msg.supports_internal_invoice
  mdl.instructions = msg.instructions
  mdl.logistics_instructions = msg.logistics_instructions
  mdl.delivery_options = msg.delivery_options
  mdl.retrieval_options = msg.retrieval_options
  mdl.pickup_options = msg.pickup_options
  mdl.borrow_options = msg.borrow_options
  # can't set automatic fields:
  # TODO
  if msg.default_supplier:
    mdl.supplier = ndb.Key(ndb_models.Supplier, msg.default_supplier)
  return mdl


class OrderSheet(messages.Message):
  id = messages.IntegerField(1)
  code = messages.StringField(2)
  name = messages.StringField(3)
  default_supplier = messages.IntegerField(4)
  visibility = messages.StringField(5)
  instructions = messages.StringField(6)
  supports_internal_invoice = messages.BooleanField(11)
  logistics_instructions = messages.StringField(7)
  delivery_options = messages.StringField(8)
  retrieval_options = messages.StringField(9)
  pickup_options = messages.StringField(10)
  borrow_options = messages.StringField(12)


############
# StaffTime #
############

def StaffTimeModelToMessage(mdl):
  s = StaffTime(
    id=mdl.key.integer_id(),
    program=mdl.program,
    description=mdl.description,
    site=mdl.site.integer_id(),
    hours=mdl.hours,
    state=mdl.state,
    miles=mdl.miles,
    position=mdl.position.integer_id(),
  )
  # any special handling, like for user objects or datetimes
  if mdl.captain:
    s.captain = mdl.captain.integer_id()
  if mdl.activity_date:
    s.activity_date = mdl.activity_date.isoformat()
  else:
    s.activity_date = ''
  return s


def StaffTimeMessageToModel(msg, mdl):
  mdl.program = msg.program
  mdl.description = msg.description
  mdl.site = ndb.Key(ndb_models.NewSite, msg.site)
  mdl.hours = msg.hours
  mdl.state = msg.state
  mdl.miles = msg.miles
  mdl.position = ndb.Key(ndb_models.StaffPosition, msg.position)
  # can't set automatic fields:
  # captain.

  if mdl.state == 'new':
    mdl.state = 'submitted'
  try:
    mdl.activity_date = datetime.date(*map(int, msg.activity_date.split('-')))
  except Exception, e:
    raise remote.ApplicationError('failed to parse date as yyyy-mm-dd: {}'.format(msg.activity_date))
  return mdl


class StaffTime(messages.Message):
  id = messages.IntegerField(1)
  program = messages.StringField(2)
  description = messages.StringField(3)
  site = messages.IntegerField(4)
  hours = messages.FloatField(5)
  captain = messages.IntegerField(6)
  activity_date = messages.StringField(7)
  state = messages.StringField(8)
  miles = messages.FloatField(9)
  position = messages.IntegerField(10)


############
# CheckRequest #
############

def CheckRequestModelToMessage(mdl):
  s = CheckRequest(
    id=mdl.key.integer_id(),
    labor_amount=mdl.labor_amount,
    description=mdl.description,
    site=mdl.site.integer_id(),
    materials_amount=mdl.materials_amount,
    food_amount=mdl.food_amount,
    address=mdl.address,
    tax_id=mdl.tax_id,
    name=mdl.name,
    state=mdl.state,
    form_of_business=mdl.form_of_business,
  )
  # any special handling, like for user objects or datetimes
  if mdl.payment_date:
    s.payment_date = mdl.payment_date.isoformat()
  else:
    s.payment_date = ''
  if mdl.captain:
    s.captain = mdl.captain.integer_id()
  return s


def CheckRequestMessageToModel(msg, mdl):
  mdl.description = msg.description
  mdl.site = ndb.Key(ndb_models.NewSite, msg.site)
  mdl.labor_amount = msg.labor_amount
  mdl.materials_amount = msg.materials_amount
  mdl.food_amount = msg.food_amount
  mdl.address = msg.address
  mdl.tax_id = msg.tax_id
  mdl.name = msg.name
  mdl.state = msg.state
  mdl.form_of_business = msg.form_of_business
  # can't set automatic fields:
  # program
  if mdl.state == 'new':
    mdl.state = 'submitted'
  if msg.captain:
    mdl.captain = ndb.Key(ndb_models.Captain, msg.captain)
  try:
    mdl.payment_date = datetime.date(*map(int, msg.payment_date.split('-')))
  except Exception, e:
    raise remote.ApplicationError('failed to parse date as yyyy-mm-dd: {}'.format(msg.payment_date))

  return mdl


class CheckRequest(messages.Message):
  id = messages.IntegerField(1)
  labor_amount = messages.FloatField(2)
  description = messages.StringField(3)
  site = messages.IntegerField(4)
  materials_amount = messages.FloatField(5)
  food_amount = messages.FloatField(6)
  address = messages.StringField(7)
  tax_id = messages.StringField(8)
  payment_date = messages.StringField(9)
  captain = messages.IntegerField(10)
  name = messages.StringField(11)
  state = messages.StringField(12)
  form_of_business = messages.StringField(14)


############
# VendorReceipt #
############

def VendorReceiptModelToMessage(mdl):
  s = VendorReceipt(
    id=mdl.key.integer_id(),
    vendor=mdl.vendor,
    description=mdl.description,
    site=mdl.site.integer_id(),
    amount=mdl.amount,
    state=mdl.state
  )
  # any special handling, like for user objects or datetimes
  if mdl.purchase_date:
    s.purchase_date = mdl.purchase_date.isoformat()
  else:
    s.purchase_date = ''
  if mdl.captain:
    s.captain = mdl.captain.integer_id()
  if mdl.supplier:
    s.supplier = mdl.supplier.integer_id()

  return s


def VendorReceiptMessageToModel(msg, mdl):
  mdl.vendor = msg.vendor
  mdl.description = msg.description
  mdl.site = ndb.Key(ndb_models.NewSite, msg.site)
  mdl.amount = msg.amount
  mdl.state = msg.state
  # can't set automatic fields
  # NONE
  if mdl.state == 'new':
    mdl.state = 'submitted'
  if msg.captain:
    mdl.captain = ndb.Key(ndb_models.Captain, msg.captain)
  if msg.supplier:
    mdl.supplier = ndb.Key(ndb_models.Supplier, msg.supplier)
  try:
    mdl.purchase_date = datetime.date(*map(int, msg.purchase_date.split('-')))
  except Exception, e:
    raise remote.ApplicationError('failed to parse date as yyyy-mm-dd: {}'.format(msg.purchase_date))
  return mdl


class VendorReceipt(messages.Message):
  id = messages.IntegerField(1)
  vendor = messages.StringField(2)
  description = messages.StringField(3)
  site = messages.IntegerField(4)
  captain = messages.IntegerField(5)
  amount = messages.FloatField(6)
  state = messages.StringField(7)
  purchase_date = messages.StringField(9)
  supplier = messages.IntegerField(10)
  # don't use program, it's automatic


############
# InKindDonation #
############

def InKindDonationModelToMessage(mdl):
  s = InKindDonation(
    id=mdl.key.integer_id(),
    labor_amount=mdl.labor_amount,
    donor_phone=mdl.donor_phone,
    description=mdl.description,
    donor_info=mdl.donor_info,
    site=mdl.site.integer_id(),
    materials_amount=mdl.materials_amount,
    state=mdl.state,
    budget=mdl.budget,
    donor=mdl.donor,
  )
  # any special handling, like for user objects or datetimes
  if mdl.donation_date:
    s.donation_date = mdl.donation_date.isoformat()
  else:
    s.donation_date = ''
  if mdl.captain:
    s.captain = mdl.captain.integer_id()
  return s


def InKindDonationMessageToModel(msg, mdl):
  mdl.labor_amount = msg.labor_amount
  mdl.donor_phone = msg.donor_phone
  mdl.description = msg.description
  mdl.donor_info = msg.donor_info
  mdl.site = ndb.Key(ndb_models.NewSite, msg.site)
  mdl.materials_amount = msg.materials_amount
  mdl.state = msg.state
  mdl.budget = msg.budget
  mdl.donor = msg.donor
  # can't set automatic fields:
  # program
  if mdl.state == 'new':
    mdl.state = 'submitted'
  if msg.captain:
    mdl.captain = ndb.Key(ndb_models.Captain, msg.captain)
  try:
    mdl.donation_date = datetime.date(*map(int, msg.donation_date.split('-')))
  except Exception, e:
    raise remote.ApplicationError('failed to parse date as yyyy-mm-dd: {}'.format(msg.donation_date))
  return mdl


class InKindDonation(messages.Message):
  id = messages.IntegerField(1)
  labor_amount = messages.FloatField(2)
  donor_phone = messages.StringField(3)
  description = messages.StringField(4)
  donor_info = messages.StringField(5)
  site = messages.IntegerField(6)
  materials_amount = messages.FloatField(7)
  donation_date = messages.StringField(8)
  captain = messages.IntegerField(9)
  state = messages.StringField(10)
  budget = messages.StringField(12)
  donor = messages.StringField(13)


############
# Item #
############

def ItemModelToMessage(mdl):
  s = Item(
    id=mdl.key.integer_id(),
    description=mdl.description,
    bar_code_number=mdl.bar_code_number,
    unit_cost=mdl.unit_cost,
    must_be_returned=mdl.must_be_returned,
    measure=mdl.measure,
    name=mdl.name,
    supplier_part_number=mdl.supplier_part_number,
    url=mdl.url,
    order_form_section=mdl.order_form_section,
  )
  # any special handling, like for user objects or datetimes
  if mdl.appears_on_order_form:
    s.appears_on_order_form = mdl.appears_on_order_form.integer_id()
  if mdl.supplier:
    s.supplier = mdl.supplier.integer_id()
  s.visible_name = mdl.VisibleName()
  s.visible_section = mdl.VisibleOrderFormSection()
  return s


def ItemMessageToModel(msg, mdl):
  mdl.description = msg.description
  mdl.bar_code_number = msg.bar_code_number
  mdl.unit_cost = msg.unit_cost
  mdl.must_be_returned = msg.must_be_returned
  mdl.measure = msg.measure
  mdl.name = msg.name
  mdl.supplier_part_number = msg.supplier_part_number
  mdl.url = msg.url
  mdl.order_form_section = msg.order_form_section
  # can't set automatic fields:
  if msg.appears_on_order_form:
    mdl.appears_on_order_form = ndb.Key(ndb_models.OrderSheet, msg.appears_on_order_form)
  if msg.supplier:
    mdl.supplier = ndb.Key(ndb_models.Supplier, msg.supplier)
  return mdl


class Item(messages.Message):
  id = messages.IntegerField(1)
  description = messages.StringField(2)
  bar_code_number = messages.IntegerField(3)
  unit_cost = messages.FloatField(4)
  appears_on_order_form = messages.IntegerField(5)
  must_be_returned = messages.StringField(6)
  measure = messages.StringField(7)
  name = messages.StringField(8)
  supplier_part_number = messages.StringField(9)
  url = messages.StringField(10)
  order_form_section = messages.StringField(11)
  supplier = messages.IntegerField(12)
  visible_name = messages.StringField(13)
  visible_section = messages.StringField(14)


############
# Order #
############

def OrderModelToMessage(mdl):
  s = Order(
    id=mdl.key.integer_id(),
    site=mdl.site.integer_id(),
    reconciliation_notes=mdl.reconciliation_notes,
    logistics_end=mdl.logistics_end,
    logistics_instructions=mdl.logistics_instructions,
    order_sheet=mdl.order_sheet.integer_id(),
    logistics_start=mdl.logistics_start,
    state=mdl.state,
    notes=mdl.notes,
    actual_total=mdl.actual_total,
    sub_total=mdl.sub_total,
  )
  # any special handling, like for user objects or datetimes
  if mdl.vendor:
    s.vendor = mdl.vendor.integer_id()
  if mdl.invoice_date:
    s.invoice_date = mdl.invoice_date.isoformat()
  else:
    s.invoice_date = ''
  if mdl.modified:
    s.modified_ago = str(datetime.datetime.now() - mdl.modified)
  else:
    s.modified_ago = ''

  return s


def OrderMessageToModel(msg, mdl):
  mdl.site = ndb.Key(ndb_models.NewSite, msg.site)
  mdl.order_sheet = ndb.Key(ndb_models.OrderSheet, msg.order_sheet)
  mdl.notes = msg.notes
  mdl.reconciliation_notes = msg.reconciliation_notes
  mdl.logistics_end = msg.logistics_end
  mdl.logistics_instructions = msg.logistics_instructions
  mdl.logistics_start = msg.logistics_start
  mdl.actual_total = msg.actual_total
  # Don't set sub_total, it's computed automatically.

  if msg.state:
    mdl.state = msg.state

  if msg.vendor:
    mdl.vendor = ndb.Key(ndb_models.Supplier, msg.vendor)

  if msg.invoice_date:
    try:
      mdl.invoice_date = datetime.date(*map(int, msg.invoice_date[:10].split('-')))
    except Exception, e:
      raise remote.ApplicationError('failed to parse invoice_date as yyyy-mm-dd: {} {}'.format(msg.invoice_date, e))

  return mdl


class Order(messages.Message):
  id = messages.IntegerField(1)
  site = messages.IntegerField(2, required=True)
  order_sheet = messages.IntegerField(3, required=True)
  reconciliation_notes = messages.StringField(4)

  # These are auto-computed in the backend.
  logistics_end = messages.StringField(5)
  logistics_instructions = messages.StringField(6)
  logistics_start = messages.StringField(7)

  notes = messages.StringField(8)
  invoice_date = messages.StringField(9)
  state = messages.StringField(10)
  vendor = messages.IntegerField(11)
  actual_total = messages.FloatField(12)
  sub_total = messages.FloatField(15)

  modified_ago = messages.StringField(13)
  editable = messages.BooleanField(14)
  # Next ID to use: 16

#############
# OrderItem #
#############

def OrderItemModelToMessage(mdl):
  s = OrderItem(
    id=mdl.key.integer_id(),
    item=mdl.item.integer_id(),
    order=mdl.order.integer_id(),
    name=mdl.name,
    quantity=mdl.quantity_float,
  )
  # any special handling, like for user objects or datetimes
  if mdl.supplier:
    s.supplier = mdl.supplier.integer_id()
  if mdl.unit_cost:
    s.unit_cost = mdl.unit_cost

  return s


def OrderItemMessageToModel(msg, mdl):
  mdl.name = msg.name
  mdl.quantity_float = msg.quantity
  if msg.item:
    mdl.item = ndb.Key(ndb_models.Item, msg.item)
  if msg.order:
    mdl.order = ndb.Key(ndb_models.Order, msg.order)
  if msg.supplier:
    mdl.supplier = ndb.Key(ndb_models.Supplier, msg.supplier)

  # can't set automatic fields: unit_cost
  return mdl


class OrderItem(messages.Message):
  id = messages.IntegerField(1)
  item = messages.IntegerField(2)
  order = messages.IntegerField(3)
  supplier = messages.IntegerField(4)
  quantity = messages.FloatField(5)
  name = messages.StringField(6)
  unit_cost = messages.FloatField(7)

############
# Delivery #
############

def DeliveryModelToMessage(mdl):
  s = Delivery(
    id=mdl.key.integer_id(),
    delivery_date=mdl.delivery_date,
    notes=mdl.notes,
    contact=mdl.contact,
    contact_phone=mdl.contact_phone,
  )
  return s


def DeliveryMessageToModel(msg, mdl):
  if msg.id:
    mdl.id = msg.id
  mdl.delivery_date = msg.delivery_date  # is a string in the datastore!
  mdl.notes = msg.notes
  mdl.contact = msg.contact
  mdl.contact_phone = msg.contact_phone
  return mdl


class Delivery(messages.Message):
  id = messages.IntegerField(1)
  # Omit the 'site' field, it's not part of the API.
  delivery_date = messages.StringField(2)
  contact = messages.StringField(3)
  contact_phone = messages.StringField(4)
  notes = messages.StringField(5)


############
# Pickup #
############

def PickupModelToMessage(mdl):
  s = Pickup(
    id=mdl.key.integer_id(),
    pickup_date=mdl.pickup_date,
    return_date=mdl.return_date,
    notes=mdl.notes,
    contact=mdl.contact,
    contact_phone=mdl.contact_phone,
  )
  return s


def PickupMessageToModel(msg, mdl):
  if msg.id:
    mdl.id = msg.id
  mdl.pickup_date = msg.pickup_date  # is a string in the datastore!
  mdl.return_date = msg.return_date  # is a string in the datastore!
  mdl.notes = msg.notes
  mdl.contact = msg.contact
  mdl.contact_phone = msg.contact_phone
  return mdl


class Pickup(messages.Message):
  id = messages.IntegerField(1)
  # Omit the 'site' field, it's not part of the API.
  pickup_date = messages.StringField(2)
  return_date = messages.StringField(3)
  contact = messages.StringField(4)
  contact_phone = messages.StringField(5)
  notes = messages.StringField(6)


############
# Borrow #
############

def BorrowModelToMessage(mdl):
  s = Borrow(
    id=mdl.key.integer_id(),
    borrow_date=mdl.borrow_date,
    return_date=mdl.return_date,
    notes=mdl.notes,
    contact=mdl.contact,
    contact_phone=mdl.contact_phone,
  )
  return s


def BorrowMessageToModel(msg, mdl):
  if msg.id:
    mdl.id = msg.id
  mdl.borrow_date = msg.borrow_date  # is a string in the datastore!
  mdl.return_date = msg.return_date  # is a string in the datastore!
  mdl.notes = msg.notes
  mdl.contact = msg.contact
  mdl.contact_phone = msg.contact_phone
  return mdl


class Borrow(messages.Message):
  id = messages.IntegerField(1)
  # Omit the 'site' field, it's not part of the API.
  borrow_date = messages.StringField(2)
  return_date = messages.StringField(3)
  contact = messages.StringField(4)
  contact_phone = messages.StringField(5)
  notes = messages.StringField(6)


############
# Retrieval #
############

def RetrievalModelToMessage(mdl):
  s = Retrieval(
    id=mdl.key.integer_id(),
    retrieval_date=mdl.retrieval_date,
    dropoff_date=mdl.dropoff_date,
    notes=mdl.notes,
    contact=mdl.contact,
    contact_phone=mdl.contact_phone,
  )
  return s


def RetrievalMessageToModel(msg, mdl):
  if msg.id:
    mdl.id = msg.id
  mdl.retrieval_date = msg.retrieval_date  # is a string in the datastore!
  mdl.dropoff_date = msg.dropoff_date  # is a string in the datastore!
  mdl.notes = msg.notes
  mdl.contact = msg.contact
  mdl.contact_phone = msg.contact_phone
  return mdl


class Retrieval(messages.Message):
  id = messages.IntegerField(1)
  # Omit the 'site' field, it's not part of the API.
  retrieval_date = messages.StringField(2)
  dropoff_date = messages.StringField(3)
  contact = messages.StringField(4)
  contact_phone = messages.StringField(5)
  notes = messages.StringField(6)


############
# SiteCaptain #
############

def SiteCaptainModelToMessage(mdl):
  s = SiteCaptain(
    id=mdl.key.integer_id(),
    site=mdl.site.integer_id(),
    captain=mdl.captain.integer_id(),
    type=mdl.type,
  )
  # any special handling, like for user objects or datetimes
  return s


def SiteCaptainMessageToModel(msg, mdl):
  if not msg.site:
    raise remote.ApplicationError('site is required')
  mdl.site = ndb.Key(ndb_models.NewSite, msg.site)
  if not msg.captain:
    raise remote.ApplicationError('captain is required')
  mdl.captain = ndb.Key(ndb_models.Captain, msg.captain)
  if not msg.type:
    raise remote.ApplicationError('type is required')
  mdl.type = msg.type
  # can't set automatic fields:
  # TODO
  return mdl


class SiteCaptain(messages.Message):
  id = messages.IntegerField(1)
  site = messages.IntegerField(2)
  captain = messages.IntegerField(3)
  type = messages.StringField(4)



############
# StaffPosition #
############


def get_date_with_rate(arr, current_rate):
  print current_rate
  for dr in (string.split() for string in arr):
    print dr
    if "{:.2f}".format(float(dr[1])) == "{:.2f}".format(float(current_rate)):
      return dr[0]
  return ""

def StaffPositionModelToMessage(mdl):
  s = StaffPosition(
    id=mdl.key.integer_id(),
    position_name = mdl.position_name,
    hourly_rate = mdl.GetHourlyRate(datetime.datetime.now()),
    mileage_rate = mdl.GetMileageRate(datetime.datetime.now())
  )

  if mdl.hourly_rate_after_date:
    s.hourly_form_date = get_date_with_rate(mdl.hourly_rate_after_date, s.hourly_rate)

  if mdl.mileage_rate_after_date:
    s.mileage_form_date =  get_date_with_rate(mdl.mileage_rate_after_date, s.mileage_rate)
  return s


def StaffPositionMessageToModel(msg, mdl):

  mdl.position_name = msg.position_name
  mdl.hourly_rate = mdl.GetHourlyRate(datetime.datetime.now())
  mdl.mileage_rate = mdl.GetMileageRate(datetime.datetime.now())

  if not msg.position_name:
    raise remote.ApplicationError('position name is required')

  if not msg.hourly_form_date:
    raise remote.ApplicationError('hourly rate after date, (hourly date) is required')

  if not msg.mileage_form_date:
    raise remote.ApplicationError('mileage rate after date, (mileage date) is required')


  msg.hourly_rate_after_date  = msg.hourly_form_date  + " " +  "{:.2f}".format(msg.hourly_rate)
  msg.mileage_rate_after_date = msg.mileage_form_date + " " + "{:.2f}".format(msg.mileage_rate)


  if not (msg.hourly_rate_after_date in mdl.hourly_rate_after_date):
    mdl.hourly_rate_after_date.insert(0, msg.hourly_rate_after_date)

  if not (msg.mileage_rate_after_date in mdl.mileage_rate_after_date):
    mdl.mileage_rate_after_date.insert(0, msg.mileage_rate_after_date)

  return mdl


class StaffPosition(messages.Message):
  id = messages.IntegerField(1)
  position_name = messages.StringField(2)

  hourly_rate_after_date = messages.StringField(3)
  hourly_rate = messages.FloatField(4)
  hourly_form_date = messages.StringField(5)

  mileage_rate_after_date = messages.StringField(6)
  mileage_rate = messages.FloatField(7)
  mileage_form_date = messages.StringField(8)


# Use the multi-line string below as a template for adding models.
# Or use model_boilerplate.py
"""
############
# Example #
############

def ExampleModelToMessage(mdl):
  s = Example(
    id=mdl.key.integer_id(),
    name=mdl.name,
  )
  # any special handling, like for user objects or datetimes
  return s

def ExampleMessageToModel(msg, mdl):
  mdl.name = msg.name
  # can't set automatic fields:
  # TODO
  return mdl

class Example(messages.Message):
  id = messages.IntegerField(1)
  name = messages.StringField(2)

"""
