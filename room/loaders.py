# Copyright 2009 Luke Stone

"""Loaders and exporters for classes in models module.

http://code.google.com/appengine/docs/python/tools/uploadingdata.html
"""

# TODO(luke): create a SafeInt() method and use it in all Exporters to avoid 
# issues with None values.  Djangoforms creates None values on empty form inputs
# instead of not setting properties (which is how the Exporter handles empties).


import csv
csv.field_size_limit(1<<20)
import base64
import datetime
import logging
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.tools import bulkloader
import main  # sets up appengine backend within Django.
import models

def StrToDate(x):
  if not x: return None
  return datetime.datetime.strptime(x, '%m/%d/%Y').date()


def DateToStr(x):
  if not x: return ''
  return x.date().strftime('%m/%d/%Y')

def StrToDateTime(x):
  if not x: return None
  return datetime.datetime.strptime(x, '%m/%d/%Y %H:%M:%S')

def DateTimeToStr(x):
  if not x: return ''
  return x.strftime('%m/%d/%Y %H:%M:%S')

def StrOrNone(s):
  if not s or s == 'None':
    return None
  return str(s)

def FloatOrNone(s):
  if s == 'None':
    return None
  s = s.strip()
  s.replace('$', '')
  return float(s)

def ToFloat(v):
  if v is None:
    return 0.
  return float(v)

def _GetObjByAttr(obj_class, attr_name, attr_value):  
  if attr_value is None:
    return None
  return obj_class.all().filter('%s = ' % attr_name, attr_value).get()

def _GetKeyForObjByAttr(obj_class, attr_name, attr_value):
  co = _GetObjByAttr(obj_class, attr_name, attr_value)
  if co is None:
    return None
  return co.key()

def GetKeyForOrderSheetByCode(name):
  return _GetKeyForObjByAttr(models.OrderSheet, 'code', name)

def GetKeyForItemByName(name):
  return _GetKeyForObjByAttr(models.Item, 'name', name)

def GetKeyForSiteByNumber(number):
  return _GetKeyForObjByAttr(models.NewSite, 'number', number)

def GetKeyByEmail(obj_class, email):
  return _GetKeyForObjByAttr(obj_class, 'email', email)

def GetUserByEmail(email):
  if email is None:
    return None
  try:
    user = users.User(email)
  except users.UserNotFoundError:
    logging.warning('User not found! (email=%r)', email)
    return None

def GetKeyForUserByEmail(obj_class, email):
  user = GetUserByEmail(email)
  if user is None:
    return None
  return _GetKeyForObjByAttr(obj_class, 'user', user)

def GetKeyForCaptainByEmail(email):
  return GetKeyByEmail(models.Captain, email)

def GetKeyForSupplierByEmail(email):
  return GetKeyByEmail(models.Supplier, email)

def GetKeyForStaffByEmail(email):
  return GetKeyByEmail(models.Staff, email)


def _GetAttrForObjByKey(attr_name, key):
  if key is None:
    return None
  res = db.get(key)
  if res and hasattr(res, attr_name):
    return getattr(res, attr_name)
  else:
    return None

def GetNumberByKey(key):
  return _GetAttrForObjByKey('number', key)

def GetCodeByKey(key):
  return _GetAttrForObjByKey('code', key)

def GetEmailByKey(key):
  return _GetAttrForObjByKey('email', key)

def GetNameByKey(key):
  return _GetAttrForObjByKey('name', key)

def GetEmailForUser(user):
  if user is None:
    return None
  return user.email()

def GetOrderHandle(key):
  if key is None:
    return None
  res = db.get(key)
  if res is None:
    return ''
  return '+++'.join((
      _GetAttrForObjByKey('number', res.site.key()),
      _GetAttrForObjByKey('code', res.order_sheet.key()),
      DateTimeToStr(res.created)
      ))

def GetKeyForOrderByHandle(handle):
  if not handle:
    return None
  s, os, cr = handle.split('+++')
  s_k = _GetObjByAttr(models.NewSite, 'number', s)
  os_k = _GetObjByAttr(models.OrderSheet, 'code', os)
  dt = StrToDateTime(cr)
  q = models.Order.all()
  q.filter('site = ', s_k)
  q.filter('order_sheet = ', os_k)
  q.filter('created = ', dt)
  o = q.get()
  if o is None:
    logging.warning('No order found for handle %s', handle)
    return None
  return o.key()

def Base64Encode(x):
  if x is None:
    return ''
  return base64.b64encode(x)

def Base64Decode(x):
  if x is None:
    return ''
  return base64.b64decode(x)


class OrderSheetLoader(bulkloader.Loader):
  def __init__(self):
    bulkloader.Loader.__init__(self, 'OrderSheet',
                               [('code', str),
                                ('name', str),
                                ('instructions', str),
                                ('delivery_options', str),
                                ])


class OrderSheetExporter(bulkloader.Exporter):
  def __init__(self):
    bulkloader.Exporter.__init__(self, 'OrderSheet',
                                 [('code', str, None),
                                  ('name', str, None),
                                  ])


class SiteLoader(bulkloader.Loader):
  def __init__(self):
    bulkloader.Loader.__init__(self, 'Site',
                                 [('number', str),
                                  ('name', str),
                                  ('street', str),
                                  ('applicant', str),
                                  ('sponsors', str),
                                  ('difficulty', str),
                                  ('postal_address', str),
                                  ('work_start', StrToDate),
                                  ('work_end', StrToDate),
                                  ('notes', str),
                                  ])


class SiteExporter(bulkloader.Exporter):
  def __init__(self):
    bulkloader.Exporter.__init__(self, 'Site',
                                 [('number', str, None),
                                  ('name', str, ''),
                                  ('street', str, ''),
                                  ('applicant', str, ''),
                                  ('sponsors', str, ''),
                                  ('difficulty', str, ''),
                                  ('postal_address', str, ''),
                                  ('work_start', DateToStr, None),
                                  ('work_end', DateToStr, None),
                                  ('notes', str, ''),
                                  ])


class NewSiteLoader(bulkloader.Loader):
  def __init__(self):
    bulkloader.Loader.__init__(self, 'NewSite',
                                 [('number', str),
                                  ('name', str),
                                  ('applicant', str),
                                  ('street_number', str),
                                  ('street', str),
                                  ('city_state_zip', str),
                                  ('city', str),
                                  ('budget', int),                                  
                                  ])


class NewSiteExporter(bulkloader.Exporter):
  def __init__(self):
    bulkloader.Exporter.__init__(self, 'NewSite',
                                 [('number', str, ''),
                                  ('name', str, ''),
                                  ('applicant', str, ''),
                                  ('street_number', str, ''),
                                  ('street', str, ''),
                                  ('city_state_zip', str, ''),
                                  ('city', str, ''),
                                  ('budget', int, 0),
                                  ])


class SiteCaptainLoader(bulkloader.Loader):
  def __init__(self):
    bulkloader.Loader.__init__(self, 'SiteCaptain',
                               [('site', GetKeyForSiteByNumber),
                                ('captain', GetKeyForCaptainByEmail),
                                ('type', str),
                                ])

  def create_entity(self, *a, **k):
    try: 
      return bulkloader.Loader.create_entity(self, *a, **k)
    except Exception, e:
      logging.warning('Error while creating entity from *a(%s) **k(%s): %s',
                      a, k, e)
      return []

class SiteCaptainExporter(bulkloader.Exporter):
  def __init__(self):
    bulkloader.Exporter.__init__(self, 'SiteCaptain',
                                 [('site', GetNumberByKey, None),
                                  ('captain', GetEmailByKey, None),
                                  ('type', str, ''),
                                  ])


class CaptainLoader(bulkloader.Loader):
  def __init__(self):
    bulkloader.Loader.__init__(self, 'Captain',
                                 [('name', str),
                                  ('email', str),
                                  ('phone1', str),
                                  ('phone2', str),
                                  ('notes', str),
                                  ])
                               

class CaptainExporter(bulkloader.Exporter):
  def __init__(self):
    bulkloader.Exporter.__init__(self, 'Captain',
                                 [('name', str, None),
                                  ('email', str, ''),
                                  ('phone1', str, ''),
                                  ('phone2', str, ''),
                                  ('notes', str, ''),
                                  ])


class StaffLoader(bulkloader.Loader):
  def __init__(self):
    bulkloader.Loader.__init__(self, 'Staff',
                                 [('name', str),
                                  ('email', str),
                                  ('notes', str),
                                  ('since', StrToDate)])


class StaffExporter(bulkloader.Exporter):
  def __init__(self):
    bulkloader.Exporter.__init__(self, 'Staff',
                                 [('name', str, None),
                                  ('email', str, ''),
                                  ('notes', str, ''),
                                  ('since', DateToStr, None)])


class SupplierLoader(bulkloader.Loader):
  def __init__(self):
    bulkloader.Loader.__init__(self, 'Supplier',
                                 [('name', str),
                                  ('email', str),
                                  ('address', str),
                                  ('phone1', str),
                                  ('phone2', str),
                                  ('notes', str),
                                  ('since', StrToDate)])


class SupplierExporter(bulkloader.Exporter):
  def __init__(self):
    bulkloader.Exporter.__init__(self, 'Supplier',
                                 [('name', str, None),
                                  ('email', str, ''),
                                  ('address', str, ''),
                                  ('phone1', str, ''),
                                  ('phone2', str, ''),
                                  ('notes', str, ''),
                                  ('since', DateToStr, None)])


class OldItemLoader(bulkloader.Loader):
  def __init__(self):
    bulkloader.Loader.__init__(self, 'Item',
                               [('bar_code_number', int),
                                ('name', str),
                                ('description', str),
                                ('measure', str),
                                ('unit_cost', FloatOrNone),
                                ('appears_on_order_form', 
                                 GetKeyForOrderSheetByCode),
                                ('supplier', GetKeyForSupplierByEmail),
                                ('supplier_part_number', str),
                                ('picture', Base64Decode),
                                ('thumbnail', Base64Decode),
                                ('url', StrOrNone),
                                ])

class ItemLoader(bulkloader.Loader):
  def __init__(self):
    bulkloader.Loader.__init__(self, 'Item',
                               [('order_form_section', str),
                                ('name', str),
                                ('description', str),
                                ('measure', str),
                                ('unit_cost', FloatOrNone),
                                ('appears_on_order_form', 
                                 GetKeyForOrderSheetByCode),
                                ])
    
    
class ItemExporter(bulkloader.Exporter):
  def __init__(self):
    bulkloader.Exporter.__init__(self, 'Item',
                                 [('bar_code_number', int, 0),
                                  ('name', str, ''),
                                  ('description', str, ''),
                                  ('measure', str, ''),
                                  ('unit_cost', str, 0.),
                                  ('appears_on_order_form', 
                                   GetNameByKey, ''),
                                  ('order_form_section', str, ''),
                                  ('supplier', 
                                   GetEmailByKey, ''),
                                  ('supplier_part_number', str, ''),
                                  ('picture', Base64Encode, ''),
                                  ('thumbnail', Base64Encode, ''),
                                  ('url', str, ''),
                                  ])
    
class InventoryItemLoader(bulkloader.Loader):
  def __init__(self):
    bulkloader.Loader.__init__(self, 'InventoryItem',
                               [('item', GetKeyForItemByName),
                                ('quantity', int),
                                ])
    
    
class InventoryItemExporter(bulkloader.Exporter):
  def __init__(self):
    bulkloader.Exporter.__init__(self, 'InventoryItem',
                                 [('item', GetNameByKey, ''),
                                  ('quantity', int, 0),
                                  ])


class OrderExporter(bulkloader.Exporter):
  def __init__(self):
    bulkloader.Exporter.__init__(self, 'Order',
                                 [('site', GetNumberByKey, None),
                                  ('order_sheet', GetCodeByKey, None),
                                  ('sub_total', ToFloat, 0),
                                  ('sales_tax', ToFloat, 0),
                                  ('grand_total', ToFloat, 0),
                                  ('notes', str, ''),
                                  ('state', str, ''),
                                  ('pickup_on', DateToStr, None),
                                  ('return_on', DateToStr, None),
                                  ('created', DateTimeToStr, None),
                                  ('created_by', GetEmailForUser, None),
                                  ('modified', DateTimeToStr, None),
                                  ('modified_by', GetEmailForUser, None),
                                  ])


class OrderLoader(bulkloader.Loader):
  def __init__(self):
    bulkloader.Loader.__init__(self, 'Order',
                                 [('site', GetKeyForSiteByNumber),
                                  ('order_sheet', GetKeyForOrderSheetByCode),
                                  ('sub_total', FloatOrNone),
                                  ('sales_tax', FloatOrNone),
                                  ('grand_total', FloatOrNone),
                                  ('notes', StrOrNone),
                                  ('state', StrOrNone),
                                  ('pickup_on', StrToDate),
                                  ('return_on', StrToDate),
                                  ('created', StrToDateTime),
                                  ('created_by', GetUserByEmail),
                                  ('modified', StrToDateTime),
                                  ('modified_by', GetUserByEmail),
                                  ])

class OrderItemExporter(bulkloader.Exporter):
  def __init__(self):
    bulkloader.Exporter.__init__(
      self, 'OrderItem',
      [('item', GetNameByKey, ''),
       ('order', GetOrderHandle, ''),
       ('quantity', int, 0),
       ('pickup_on', DateToStr, None),
       ('return_on', DateToStr, None)])
    

class OrderItemLoader(bulkloader.Loader):
  def __init__(self):
    bulkloader.Loader.__init__(self, 'OrderItem',
                               [('item', GetKeyForItemByName),
                                ('order', GetKeyForOrderByHandle),
                                ('quantity', int),
                                ('pickup_on', StrToDate),
                                ('return_on', StrToDate)])
                               
                               

exporters = [
  OrderSheetExporter, 
  SiteExporter, 
  NewSiteExporter, 
  CaptainExporter, 
  SiteCaptainExporter, 
  StaffExporter, 
  SupplierExporter, 
  ItemExporter,
  InventoryItemExporter,
  OrderExporter,
  OrderItemExporter,
  ]
loaders = [
  OrderSheetLoader, 
  SiteLoader, 
  NewSiteLoader, 
  CaptainLoader, 
  SiteCaptainLoader, 
  StaffLoader, 
  SupplierLoader, 
  ItemLoader,
  InventoryItemLoader,
  OrderLoader,
  OrderItemLoader,
  ]
