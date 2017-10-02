import datetime
import logging

import six
from google.appengine.ext import ndb
from protorpc import message_types
from protorpc import messages
from protorpc import remote
from protorpc.wsgi import service

import common
import ndb_models

package = 'rooms'


class GenericResponse(messages.Message):
  message = messages.StringField(1)


class SimpleId(messages.Message):
  id = messages.IntegerField(1, required=True)


class Choice(messages.Message):
  id = messages.IntegerField(1, required=True)
  label = messages.StringField(2)


class Choices(messages.Message):
  choice = messages.MessageField(Choice, 1, repeated=True)


class StaffPosition(messages.Message):
  key = messages.IntegerField(1)
  position_name = messages.StringField(2)
  hourly_rate = messages.FloatField(3)


class Program(messages.Message):
  year = messages.IntegerField(1)
  name = messages.StringField(2)
  site_number_prefix = messages.StringField(3)
  status = messages.StringField(4)


class Programs(messages.Message):
  program = messages.MessageField(Program, 1, repeated=True)


################
# Jurisdiction #
################

def _JurisdictionModelToMessage(mdl):
  s = Jurisdiction(
    name=mdl.name,
    id=mdl.key.integer_id(),
  )
  return s


def _JurisdictionMessageToModel(msg, mdl):
  mdl.name = msg.name
  return mdl


class Jurisdiction(messages.Message):
  id = messages.IntegerField(1)
  name = messages.StringField(2)


#########
# Staff #
#########

def _StaffModelToMessage(mdl):
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


def _StaffMessageToModel(msg, mdl):
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

def _CaptainModelToMessage(mdl):
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


def _CaptainMessageToModel(msg, mdl):
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

def _SupplierModelToMessage(mdl):
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


def _SupplierMessageToModel(msg, mdl):
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

def _NewSiteModelToMessage(mdl):
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


def _NewSiteMessageToModel(msg, mdl):
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

def _SiteModelToMessage(mdl):
  s = Site(
    id=mdl.key.integer_id(),
    number=mdl.number,
  )
  # Any special handling, like for user objects or datetimes
  return s


def _SiteMessageToModel(msg, mdl):
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

def _OrderSheetModelToMessage(mdl):
  s = OrderSheet(
    id=mdl.key.integer_id(),
    code=mdl.code,
    name=mdl.name,
    visibility=mdl.visibility,
    instructions=mdl.instructions,
    logistics_instructions=mdl.logistics_instructions,
    delivery_options=mdl.delivery_options,
    retrieval_options=mdl.retrieval_options,
    pickup_options=mdl.pickup_options,
  )
  # any special handling, like for user objects or datetimes
  if mdl.default_supplier:
    s.default_supplier = mdl.default_supplier.integer_id()
  return s


def _OrderSheetMessageToModel(msg, mdl):
  mdl.code = msg.code
  mdl.name = msg.name
  mdl.visibility = msg.visibility
  mdl.instructions = msg.instructions
  mdl.logistics_instructions = msg.logistics_instructions
  mdl.delivery_options = msg.delivery_options
  mdl.retrieval_options = msg.retrieval_options
  mdl.pickup_options = msg.pickup_options
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
  logistics_instructions = messages.StringField(7)
  delivery_options = messages.StringField(8)
  retrieval_options = messages.StringField(9)
  pickup_options = messages.StringField(10)


############
# StaffTime #
############

def _StaffTimeModelToMessage(mdl):
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


def _StaffTimeMessageToModel(msg, mdl):
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

def _CheckRequestModelToMessage(mdl):
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


def _CheckRequestMessageToModel(msg, mdl):
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

def _VendorReceiptModelToMessage(mdl):
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


def _VendorReceiptMessageToModel(msg, mdl):
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

def _InKindDonationModelToMessage(mdl):
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


def _InKindDonationMessageToModel(msg, mdl):
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

def _ItemModelToMessage(mdl):
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


def _ItemMessageToModel(msg, mdl):
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

def _OrderModelToMessage(mdl):
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
  )
  # any special handling, like for user objects or datetimes
  if mdl.vendor:
    s.vendor = mdl.vendor.integer_id()
  if mdl.invoice_date:
    s.invoice_date = mdl.invoice_date.isoformat()
  else:
    s.invoice_date = ''

  return s


def _OrderMessageToModel(msg, mdl):
  mdl.site = ndb.Key(ndb_models.NewSite, msg.site)
  mdl.order_sheet = ndb.Key(ndb_models.OrderSheet, msg.order_sheet)
  mdl.notes = msg.notes
  mdl.reconciliation_notes = msg.reconciliation_notes
  mdl.logistics_end = msg.logistics_end
  mdl.logistics_instructions = msg.logistics_instructions
  mdl.logistics_start = msg.logistics_start
  mdl.actual_total = msg.actual_total

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


#############
# OrderItem #
#############

def _OrderItemModelToMessage(mdl):
  s = OrderItem(
    id=mdl.key.integer_id(),
    item=mdl.item.integer_id(),
    order=mdl.order.integer_id(),
    name=mdl.name,
    quantity=mdl.quantity_float,
  )
  # any special handling, like for user objects or datetimes
  if mdl.supplier:
    supplier = mdl.supplier.integer_id(),

  return s


def _OrderItemMessageToModel(msg, mdl):
  mdl.name = msg.name
  mdl.quantity_float = msg.quantity
  mdl.item = ndb.Key(ndb_models.Item, msg.item)
  mdl.order = ndb.Key(ndb_models.Order, msg.order)
  # can't set automatic fields:
  if msg.supplier:
    mdl.supplier = ndb.Key(ndb_models.Supplier, msg.supplier)
  return mdl


class OrderItem(messages.Message):
  id = messages.IntegerField(1)
  item = messages.IntegerField(2)
  order = messages.IntegerField(3)
  supplier = messages.IntegerField(4)
  quantity = messages.FloatField(5)
  name = messages.StringField(6)


############
# Delivery #
############

def _DeliveryModelToMessage(mdl):
  s = Delivery(
    id=mdl.key.integer_id(),
    delivery_date=mdl.delivery_date,
    notes=mdl.notes,
    contact=mdl.contact,
    contact_phone=mdl.contact_phone,
  )
  return s


def _DeliveryMessageToModel(msg, mdl):
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

def _PickupModelToMessage(mdl):
  s = Pickup(
    id=mdl.key.integer_id(),
    pickup_date=mdl.pickup_date,
    return_date=mdl.return_date,
    notes=mdl.notes,
    contact=mdl.contact,
    contact_phone=mdl.contact_phone,
  )
  return s


def _PickupMessageToModel(msg, mdl):
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
# Retrieval #
############

def _RetrievalModelToMessage(mdl):
  s = Retrieval(
    id=mdl.key.integer_id(),
    retrieval_date=mdl.retrieval_date,
    dropoff_date=mdl.dropoff_date,
    notes=mdl.notes,
    contact=mdl.contact,
    contact_phone=mdl.contact_phone,
  )
  return s


def _RetrievalMessageToModel(msg, mdl):
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


#######################################
# Non-CRUD API and composite messages #
#######################################

class OrderFormChoice(messages.Message):
  id = messages.IntegerField(1)
  name = messages.StringField(2)
  code = messages.StringField(3)
  visibility = messages.StringField(4)


class OrderFormChoices(messages.Message):
  order_form = messages.MessageField(OrderFormChoice, 1, repeated=True)


class OrderFormDetail(messages.Message):
  order_sheet = messages.MessageField(OrderSheet, 1)
  sorted_items = messages.MessageField(Item, 2, repeated=True)


class OrderFull(messages.Message):
  order = messages.MessageField(Order, 1, required=True)
  order_items = messages.MessageField(OrderItem, 2, repeated=True)
  delivery = messages.MessageField(Delivery, 3)
  pickup = messages.MessageField(Pickup, 4)
  retrieval = messages.MessageField(Retrieval, 5)
  id = messages.IntegerField(6)


# Use the multi-line string below as a template for adding models.
# Or use model_boilerplate.py
"""
############
# Example #
############

def _ExampleModelToMessage(mdl):
  s = Example(
    id=mdl.key.integer_id(),
    name=mdl.name,
  )
  # any special handling, like for user objects or datetimes
  return s

def _ExampleMessageToModel(msg, mdl):
  mdl.name = msg.name
  # can't set automatic fields:
  # TODO
  return mdl

class Example(messages.Message):
  id = messages.IntegerField(1)
  name = messages.StringField(2)

"""

basic_crud_config = (
  (Jurisdiction, ndb_models.Jurisdiction,
   _JurisdictionMessageToModel, _JurisdictionModelToMessage),
  (Staff, ndb_models.Staff,
   _StaffMessageToModel, _StaffModelToMessage),
  (Captain, ndb_models.Captain,
   _CaptainMessageToModel, _CaptainModelToMessage),
  (Supplier, ndb_models.Supplier,
   _SupplierMessageToModel, _SupplierModelToMessage),
  (NewSite, ndb_models.NewSite,
   _NewSiteMessageToModel, _NewSiteModelToMessage),
  (Site, ndb_models.NewSite,  # TODO: remove
   _SiteMessageToModel, _SiteModelToMessage),
  (OrderSheet, ndb_models.OrderSheet,
   _OrderSheetMessageToModel, _OrderSheetModelToMessage),
  (StaffTime, ndb_models.StaffTime,
   _StaffTimeMessageToModel, _StaffTimeModelToMessage),
  (CheckRequest, ndb_models.CheckRequest,
   _CheckRequestMessageToModel, _CheckRequestModelToMessage),
  (VendorReceipt, ndb_models.VendorReceipt,
   _VendorReceiptMessageToModel, _VendorReceiptModelToMessage),
  (InKindDonation, ndb_models.InKindDonation,
   _InKindDonationMessageToModel, _InKindDonationModelToMessage),
  (Item, ndb_models.Item,
   _ItemMessageToModel, _ItemModelToMessage),
  (Order, ndb_models.Order,
   _OrderMessageToModel, _OrderModelToMessage),

  #  (Example, ndb_models.Example,
  # _ExampleMessageToModel, _ExampleModelToMessage),
)


class _GeneratedCrudApi(remote._ServiceClass):  # sorry. but 'remote' used metaclass so we have to as well.
  """Metaclass for adding CRUD methods to a service, based on a config."""

  def __new__(mcs, name, bases, dct):
    """Set up mcs dict so it will have methods wrapped by remote.method.

    This is necessary to get the protorpc service to notice the methods, since
    it does so in remote._Service metaclass.
    """

    def makeBasicCrud(msg_name, msg_cls, mdl_cls, g2d, d2g):
      """Create functions for three basic CRU operations on a model.

      CRU == Create, Read, Update.  

      We don't do Delete because it may leave dangling references.

      Args:
        msg_name: name of the Message
        msg_cls: class of the message, defined above
        mdl_cls: class of the ndb model
        g2d: function to copy a message into a model.  g2d(msg, mdl)
        d2g: function to copy a model into a new message.  msg = d2g(mdl)

      Returns:
        three CRU functions, each usable as a Protorpc remote method
      """

      def mdl_read(self, request):
        self._authorize_staff()
        if not request.id:
          raise remote.ApplicationError('id is required')
        mdl = ndb.Key(mdl_cls, request.id).get()
        if not mdl:
          raise remote.ApplicationError(
            'No {} found with key {}'.format(msg_name, request.id))
        return d2g(mdl)

      def mdl_create(self, request):
        self._authorize_staff()
        if request.id:
          raise remote.ApplicationError(
            'Must not include id with create requests')
        mdl = mdl_cls()
        g2d(request, mdl)
        mdl.put()
        return d2g(mdl)

      def mdl_update(self, request):
        self._authorize_staff()
        if not request.id:
          raise remote.ApplicationError('id is required')
        mdl = ndb.Key(mdl_cls, request.id).get()
        if not mdl:
          raise remote.ApplicationError(
            'No {} found with key {}'.format(msg_name, request.id))
        g2d(request, mdl)
        mdl.put()
        return d2g(mdl)

      return mdl_create, mdl_read, mdl_update

    # Create the CRU methods for each model and stick them in the class dict,
    # where the protorpc service will find them.
    # See remote._ServiceClass.__new__ and look for __remote_methods.
    for msg, mdl, g2d, d2g in basic_crud_config:
      msg_name = msg.__name__
      mdl_create, mdl_read, mdl_update = makeBasicCrud(msg_name, msg, mdl, g2d, d2g)

      msg_x2_wrapper = remote.method(msg, msg)
      id_msg_wrapper = remote.method(SimpleId, msg)

      func_name = '{}_create'.format(msg_name.lower())
      mdl_create.__name__ = func_name
      dct[func_name] = msg_x2_wrapper(mdl_create)

      func_name = '{}_read'.format(msg_name.lower())
      mdl_read.__name__ = func_name
      dct[func_name] = id_msg_wrapper(mdl_read)

      func_name = '{}_update'.format(msg_name.lower())
      mdl_update.__name__ = func_name
      dct[func_name] = msg_x2_wrapper(mdl_update)

    return type.__new__(mcs, name, bases, dct)


class RoomApi(six.with_metaclass(_GeneratedCrudApi, remote.Service)):
  """Protorpc service implementing a CRUD API for ROOM models"""

  # Stash the request state so we can get at the HTTP headers later.
  def initialize_request_state(self, request_state):
    self.rs = request_state

  def _authorize_staff(self):
    """Simply call this to ensure that the user has a Staff record.

    Raises:
      remote.ApplicationError if the user is not Staff.
    """
    user, status = common.GetUser(self.rs)
    if user and user.staff:
      return
    raise remote.ApplicationError('Must be staff to use this API.')

  def _authorize_user(self):
    """Simply call this to ensure that the user has a ROOMS record.

    Raises:
      remote.ApplicationError if the user is not Staff or Captain.
    """
    user, status = common.GetUser(self.rs)
    if user and (user.staff or user.captain):
      return
    raise remote.ApplicationError('Must be a ROOMS user to use this API.')

  @remote.method(message_types.VoidMessage,
                 message_types.VoidMessage)
  def ehlo(self, request):
    logging.info('ehlo')
    return message_types.VoidMessage()

  # This needs an update for the new encoding for StaffPosition rates.  Per issue 238.
  # If it's used at all...
  @remote.method(StaffPosition,
                 GenericResponse)
  def staffposition_put(self, request):
    self._authorize_staff()
    sp = ndb_models.StaffPosition(position_name=request.position_name,
                                  hourly_rate=request.hourly_rate)
    if request.key:
      sp.key = ndb.Key(ndb_models.StaffPosition, request.key)
      sp.put()
    return GenericResponse()

  @remote.method(Program,
                 GenericResponse)
  def program_put(self, request):
    self._authorize_staff()
    resp = GenericResponse()
    try:
      sp = ndb_models.Program(name=request.name,
                              year=request.year,
                              site_number_prefix=request.site_number_prefix,
                              status=request.status)
      sp.put()
      resp.message = 'OK'
    except Exception, e:
      resp.message = str(e)

    return resp

  @remote.method(message_types.VoidMessage,
                 Programs)
  def program_list(self, request):
    programs = Programs()
    for p in ndb_models.Program.query():
      programs.program.append(Program(name=p.name, year=p.year))
    return programs

  @remote.method(message_types.VoidMessage,
                 OrderFormChoices)
  def order_form_choices(self, request):
    res = OrderFormChoices()
    for m in ndb_models.OrderSheet.query():
      f = OrderFormChoice(
        id=m.key.integer_id(), name=m.name,
        code=m.code, visibility=m.visibility)
      res.order_form.append(f)
    return res

  @remote.method(SimpleId, OrderFormDetail)
  def order_form_detail(self, request):
    res = OrderFormDetail()
    if not request.id:
      raise remote.ApplicationError('id is required')
    key = ndb.Key(ndb_models.OrderSheet, request.id)
    mdl = key.get()
    if not mdl:
      raise remote.ApplicationError(
        'No OrderSheet found with key {}'.format(request.id))
    res.order_sheet = _OrderSheetModelToMessage(mdl)
    ims = list(ndb_models.Item.query(ndb_models.Item.appears_on_order_form == key))
    ndb_models._SortItemsWithSections(ims)
    for im in ims:
      i = _ItemModelToMessage(im)
      res.sorted_items.append(i)
    return res

  @remote.method(SimpleId, OrderFull)
  def order_full_read(self, request):
    self._authorize_staff()
    res = OrderFull()
    order_key = ndb.Key(ndb_models.Order, request.id)
    order_mdl = order_key.get()
    if order_mdl is None:
      raise remote.ApplicationError(
        'No Order found with key {}'.format(request.id))
    res.id = order_key.integer_id()
    res.order = _OrderModelToMessage(order_mdl)

    for oi_mdl in ndb_models.OrderItem.query(ndb_models.OrderItem.order == order_key):
      res.order_items.append(_OrderItemModelToMessage(oi_mdl))

    join_mdl = ndb_models.OrderDelivery.query(ndb_models.OrderDelivery.order == order_key).get()
    if join_mdl is not None:
      res.delivery = _DeliveryModelToMessage(join_mdl.delivery.get())

    join_mdl = ndb_models.OrderPickup.query(ndb_models.OrderPickup.order == order_key).get()
    if join_mdl is not None:
      res.pickup = _PickupModelToMessage(join_mdl.pickup.get())

    join_mdl = ndb_models.OrderRetrieval.query(ndb_models.OrderRetrieval.order == order_key).get()
    if join_mdl is not None:
      res.retrieval = _RetrievalModelToMessage(join_mdl.retrieval.get())

    return res

  def _order_full_put(self, request):
    # TODO ndb.start_transaction ...
    order = _OrderMessageToModel(request.order, ndb_models.Order())
    sub_total = 0.
    for oimsg in request.order_items:
      if oimsg.quantity:
        item = ndb.Key(ndb_models.Item, oimsg.item).get()  # TODO: get_multi
        if item.unit_cost:
          sub_total += oimsg.quantity * item.unit_cost
    order.sub_total = sub_total
    if not order.state:
      order.state = 'Received'
    order.put()

    if request.delivery:
      delivery = _DeliveryMessageToModel(request.delivery,
                                         ndb_models.Delivery(site=order.site))
      delivery.put()
      ndb_models.OrderDelivery(order=order.key, delivery=delivery.key).put()
    if request.pickup:
      pickup = _PickupMessageToModel(request.pickup,
                                     ndb_models.Pickup(site=order.site))
      pickup.put()
      ndb_models.OrderPickup(order=order.key, pickup=pickup.key).put()
    if request.retrieval:
      retrieval = _RetrievalMessageToModel(request.retrieval,
                                           ndb_models.Retrieval(site=order.site))
      retrieval.put()
      ndb_models.OrderRetrieval(order=order.key, retrieval=retrieval.key).put()

    for oimsg in request.order_items:
      oimsg.order = order.key.integer_id()
      _OrderItemMessageToModel(oimsg, ndb_models.OrderItem()).put()  # TODO: put_multi

  @remote.method(OrderFull, message_types.VoidMessage)
  def order_full_create(self, request):
    self._authorize_staff()
    if request.id:
      raise remote.ApplicationError('must not have id in create')
    self._order_full_put(request)
    return message_types.VoidMessage()

  @remote.method(OrderFull, message_types.VoidMessage)
  def order_full_update(self, request):
    self._authorize_staff()
    if not request.id:
      raise remote.ApplicationError('id is required')
    mdl = ndb.Key(ndb_models.Order, request.id).get()
    if not mdl:
      raise remote.ApplicationError(
        'No {} found with key {}'.format(Order, request.id))
    self._order_full_put(request)
    return message_types.VoidMessage()

  # # # # # # # # # #
  #     Choices     #
  # # # # # # # # # #
  # These APIs exist to populate drop-down selections in UI.
  # Used for models that have foreign keys.

  @remote.method(message_types.VoidMessage,
                 Choices)
  def captain_choices_read(self, request):
    choices = Choices()
    for mdl in ndb_models.Captain.query().order(ndb_models.Supplier.name):
      choices.choice.append(Choice(id=mdl.key.integer_id(), label=mdl.name))
    return choices

  @remote.method(message_types.VoidMessage,
                 Choices)
  def supplier_choices_read(self, request):
    choices = Choices()
    for mdl in ndb_models.Supplier.query(ndb_models.Supplier.active == 'Active').order(ndb_models.Supplier.name):
      choices.choice.append(Choice(id=mdl.key.integer_id(), label=mdl.name))
    return choices

  @remote.method(message_types.VoidMessage,
                 Choices)
  def staffposition_choices_read(self, request):
    choices = Choices()
    for mdl in ndb_models.StaffPosition.query().order(ndb_models.StaffPosition.position_name):
      choices.choice.append(Choice(id=mdl.key.integer_id(), label=mdl.position_name))
    return choices

  @remote.method(message_types.VoidMessage,
                 Choices)
  def jurisdiction_choices_read(self, request):
    choices = Choices()
    for mdl in ndb_models.Jurisdiction.query().order(ndb_models.Jurisdiction.name):
      choices.choice.append(Choice(id=mdl.key.integer_id(), label=mdl.name))
    return choices

  @remote.method(message_types.VoidMessage,
                 Choices)
  def ordersheet_choices_read(self, request):
    choices = Choices()
    for mdl in ndb_models.OrderSheet.query().order(ndb_models.OrderSheet.name):
      choices.choice.append(Choice(id=mdl.key.integer_id(), label=mdl.name))
    return choices


application = service.service_mapping(RoomApi, r'/wsgi_service')
