# Copyright 2009 Luke Stone

"""Models defining all objects in the database."""

# TODO: factor out a common Person class from Captain, Staff, Supplier

import datetime
import logging
import math
from appengine_django.models import BaseModel
from google.appengine.ext import db

SALES_TAX_RATE = 0.0925

class Captain(BaseModel):
    """A work captain."""    
    name = db.StringProperty(required=True)  # "Joe User"
    # Using the UserProperty seems to be more hassle than it's worth.
    # I was getting errors about users that didn't exist when loading sample 
    # data.
    email = db.EmailProperty()  # "joe@user.com"
    phone1 = db.PhoneNumberProperty()  
    phone1.verbose_name = 'Preferred Phone (deprecated)'
    phone2 = db.PhoneNumberProperty()  
    phone2.verbose_name = 'Backup Phone (deprecated)'
    phone_mobile = db.StringProperty()
    phone_work = db.StringProperty()
    phone_home = db.StringProperty()
    phone_fax = db.StringProperty()
    phone_other = db.StringProperty()
    tshirt_size = db.StringProperty(choices=(
            'Small',
            'Medium',
            'Large',
            'X-Large',
            '2XL',
            '3XL'))
    notes = db.TextProperty()
    last_welcome = db.DateTimeProperty()
    modified = db.DateTimeProperty(auto_now=True)
    last_editor = db.UserProperty(auto_current_user=True)
    search_prefixes = db.StringListProperty()

    def put(self, *a, **k):
        self.email = self.email.lower()
        prefixes = set()
        if self.name:
            prefixes.add(self.name)
            for part in self.name.split():                
                prefixes.add(part)
                for i in xrange(1, 7):                    
                    prefixes.add(part[:i])
            if self.email:
                prefixes.add(self.email)
                for i in xrange(1, 7):                    
                    prefixes.add(self.email[:i])
        self.search_prefixes = [p.lower() for p in prefixes]
        super(BaseModel, self).put(*a, **k)

    def __unicode__(self):
        return self.name

    def Label(self):
        return "%s <%s>" % (self.name, self.email)
        

class Site(BaseModel):
    """A work site."""
    # "10001DAL" reads: 2010, #001, Daly City
    number = db.StringProperty(required=True)  
    number.unique = True
    name = db.StringProperty()  # "Belle Haven"
    name.verbose_name = 'Recipient Name'
    street = db.StringProperty()  # Not full street address, for privacy.
    applicant = db.StringProperty()
    applicant.verbose_name = 'Applicant Contact'
    sponsors = db.StringProperty()
    difficulty = db.StringProperty()     
    postal_address = db.PostalAddressProperty()  # Full street address.
    work_start = db.DateProperty()
    work_end = db.DateProperty()
    notes = db.TextProperty()     

    def __unicode__(self):
        return 'Site #%s | %s' % (self.key().id(), self.name)

class NewSite(BaseModel):
    """A work site."""
    # "10001DAL" reads: 2010, #001, Daly City
    number = db.StringProperty(required=True)  
    number.unique = True
    program = db.StringProperty()
    name = db.StringProperty()  # "Belle Haven"
    name.verbose_name = 'Recipient Name'
    # sites entered in 2010 do not have this field set explicitly
    year = db.IntegerProperty(default=2011)  
    applicant = db.StringProperty()
    applicant.verbose_name = 'Applicant Contact'
    applicant_home_phone = db.StringProperty()
    applicant_work_phone = db.StringProperty()
    applicant_mobile_phone = db.StringProperty()
    applicant_email = db.StringProperty()
    rating = db.StringProperty()
    roof = db.StringProperty()
    rrp_test = db.StringProperty()
    rrp_level = db.StringProperty()
    jurisdiction = db.StringProperty()
    scope_of_work = db.TextProperty()
    sponsor = db.StringProperty()
    street_number = db.StringProperty()
    street_number.verbose_name = "Street Address"
    street_number.help_text = "Full street address like 960 Main Street, Apt 4"
    city_state_zip = db.StringProperty()  
    city_state_zip.help_text = "City State Zip, like Menlo Park CA 94025"
    budget = db.IntegerProperty(default=0)
    announcement_subject = db.StringProperty(default='Nothing Needs Attention')
    announcement_body = db.TextProperty(
        default="Pat yourself on the back - no items need attention.\n"
	"You have a clean bill of health.")
    search_prefixes = db.StringListProperty()

    class ActiveItems(object):
        """Access user-input records with state and modified fields."""
        def __init__(self, query):
            """query: a bound backreference like self.order_set"""
            self._query = query.filter(
                'state != ', 'new').filter('state !=', 'deleted')
                        
        def Count(self):
            return self._query.count()
        
        def Items(self):
            for item in sorted(self._query, 
                               key=lambda o: o.modified, reverse=True):
                yield item

        def __iter__(self):
            return self.Items()

    @property
    def IsCDBG(self):
        return 'CDBG' in self.jurisdiction

    @property
    def ContactPerson(self):
        if self.applicant:
            return self.applicant
        return self.name

    @property 
    def Orders(self):
        return self.ActiveItems(self.order_set)

    @property 
    def CheckRequests(self):
        return self.ActiveItems(self.checkrequest_set)

    @property 
    def VendorReceipts(self):
        return self.ActiveItems(self.vendorreceipt_set)

    @property 
    def InKindDonations(self):
        return self.ActiveItems(self.inkinddonation_set)

    @property
    def ScopeOfWork(self):
        if self.scope_of_work:
            return self.scope_of_work
        sow = ''
        for o in self.order_set:
            if o.order_sheet.name == 'Scope of Work':
                sow = o.notes
        self.scope_of_work = sow
        self.put()
        return sow

    def ProgramFromNumber(self):
        year = '20' + self.number[0:2]
        mode = self.number[2]
        program = None
        if mode == '0':
            program = year + ' NRD'
        elif mode == '1':
            program = year + ' NRD'
        elif mode == '3':
            program = year + ' Misc'
        elif mode == '5':
            program = year + ' Safe'
        elif mode == '6':
            program = year + ' Safe'
        elif mode == '7':
            program = year + ' Energy'
        elif mode == '8':
            program = year + ' Teambuild'
        elif mode == '9':
            program = year + ' Youth'
        elif mode == 'Z':
            program = year + ' Test'
        else:
            logging.warn('no program for site number %s', self.number)
        return program

    def SaveTheChildren(self):
      for child in (self.order_set, self.checkrequest_set, 
                    self.vendorreceipt_set, self.inkinddonation_set):
        for obj in child:
          obj.put()

    def put(self, *a, **k):
        self.program = self.ProgramFromNumber()
        prefixes = set()
        for f in self.name, self.applicant, self.street_number:
            if not f:
                continue
            prefixes.add(f)
            for part in f.split():      
                prefixes.add(part)
                for i in xrange(1, 7):                    
                    prefixes.add(part[:i])
                
        if self.number:
            prefixes.add(self.number)
            for i in xrange(1, 7):                    
                prefixes.add(self.number[:i])
                prefixes.add(self.number[2:2+i])
                prefixes.add(self.number[5:5+i])
        self.search_prefixes = [p.lower() for p in prefixes]
        logging.info('prefixes for %s: %s', self.number, self.search_prefixes)
        super(BaseModel, self).put(*a, **k)
        self.SaveTheChildren()

    def Label(self):
        return "%s %s" % (self.number, self.name)

    def __unicode__(self):
        """Only works if self has been saved."""
        return 'Site #%s | %s' % (self.number, self.name)

    def StreetAddress(self):
        return '%s, %s' % (' '.join(self.street_number.split()), 
                           ' '.join(self.city_state_zip.split()))

    def NeedsAttention(self):
        return self.announcement_subject is not None
    
    def OrderTotal(self):
        """Only works if self has been saved."""    
        cost = sum(order.GrandTotal() for order in self.Orders)
        return cost

    @property 
    def order_total(self):
        if not hasattr(self, '_order_total'):
            self._order_total = self.OrderTotal()
        return self._order_total

    def CheckRequestTotal(self):
        """Only works if self has been saved."""    
        return sum(cr.Total() or 0 for cr in self.CheckRequests)

    def VendorReceiptTotal(self):
        """Only works if self has been saved."""    
        return sum(cr.amount or 0 for cr in self.VendorReceipts)

    def InKindDonationTotal(self):
        """Only works if self has been saved."""    
        return sum(cr.Total() or 0 for cr in self.InKindDonations)

    def Expenses(self):
        return (self.order_total + 
                self.CheckRequestTotal() + 
                self.VendorReceiptTotal())

    def BudgetRemaining(self):
        if self.budget:
            return self.budget - self.Expenses()
        else:
            return 0.

    @property 
    def budget_remaining(self):
        if not hasattr(self, '_budget_remaining'):
            self._budget_remaining = self.BudgetRemaining()
        return self._budget_remaining

    @property
    def in_the_red(self):
        return self.budget_remaining < 0

    def BudgetStatement(self):
        if self.BudgetRemaining() > 0:
            return '$%0.2f unspent budget' % self.BudgetRemaining()
        else:
            return '$%0.2f over budget' % (-1 * self.BudgetRemaining())



class SiteCaptain(BaseModel):
    """Associates a site and a Captain."""
    site = db.ReferenceProperty(NewSite, required=True)
    captain = db.ReferenceProperty(Captain, required=True)
    type = db.StringProperty(choices=(
            'Construction',
            'Team',
            'Volunteer',
            ))


class Staff(BaseModel):
    """A RTP staff member."""
    name = db.StringProperty()
    email = db.EmailProperty()
    email.unique = True
    email.required = True
    program_selected = db.StringProperty()
    user = db.UserProperty()
    last_welcome = db.DateTimeProperty()
    notes = db.TextProperty()
    since = db.DateProperty(auto_now_add=True)

    def __unicode__(self):
        return self.name

    def put(self, *a, **k):
        self.email = self.email.lower()
        super(BaseModel, self).put(*a, **k)
        

class Supplier(BaseModel):
    """A supplier of Items."""
    # TODO: fax, contact name vs. supplier name, 
    name = db.StringProperty()
    name.unique = True
    name.required = True
    email = db.EmailProperty()
    address = db.PostalAddressProperty()
    phone1 = db.PhoneNumberProperty()
    phone2 = db.PhoneNumberProperty()
    notes = db.TextProperty()
    since = db.DateProperty(auto_now_add=True)
    active = db.StringProperty(choices=('Active', 'Inactive'), 
                               default='Active')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class OrderSheet(BaseModel):
    """Set of items commonly ordered together.

    Corresponds to one of the old paper forms, like the Cleaning Supplies form.
    """
    name = db.StringProperty()    
    name.unique = True
    visibility = db.StringProperty(choices=('Everyone', 'Staff Only'), 
                                   default='Everyone')
    supports_extra_name_on_order = db.BooleanProperty(default=False)
    code =  db.StringProperty()    
    code.unique = True
    code.verbose_name = 'Three-letter code like LUM for Lumber'
    instructions = db.TextProperty(default='')
    instructions.verbose_name = (
        'Instructions to Captain, appears on order form')
    logistics_instructions = db.TextProperty(default='')
    logistics_instructions.verbose_name = (
        'Instructions to Captain, appears on logistics form')
    default_supplier = db.ReferenceProperty(Supplier)
    default_supplier.verbose_name = (
        'Default Supplier, used if Item\'s supplier is not set.')
    # Choose one of the next three.
    delivery_options = db.StringProperty(choices=['Yes', 'No'], default='No')
    delivery_options.verbose_name = ('Allow Captain to select Delivery to site')
    pickup_options = db.StringProperty(choices=['Yes', 'No'], default='No')
    pickup_options.verbose_name = (
        'Allow Captain to select Pick-up from RTP warehouse')
    retrieval_options = db.StringProperty(choices=['Yes', 'No'], default='No')
    retrieval_options.verbose_name = ('Drop-off and retrieval (like debris box)'
                                      '  Note: do not set this with either'
                                      ' delivery or pick-up')

    def __unicode__(self):
      return '%s' % (self.name)

    def HasLogistics(self):
        return (self.delivery_options == 'Yes' or 
                self.pickup_options == 'Yes' or 
                self.retrieval_options == 'Yes')


class Item(BaseModel):
    """Represents a type of thing that may in the inventory."""
    bar_code_number = db.IntegerProperty()
    bar_code_number.unique = True    
    name = db.StringProperty(required=True)
    name.unique = True
    appears_on_order_form = db.ReferenceProperty(OrderSheet)
    order_form_section = db.StringProperty()
    description = db.StringProperty()
    # 'Each' 'Box' 'Pair' etc
    measure = db.StringProperty(
        choices=('Each', 'Roll', 'Bottle', 'Box', 'Pair', 'Board', 'Bundle',
                 'Bag', 'Ton', 'Yard', 'Sheet', 'Cartridge', 'Tube', 'Tub',
                 'Sq. Yds.', 'Gallon', 'Section', 'Home', 'Box', 'Drop-off',
                 '', 'Other'))
    # Dollars.
    unit_cost = db.FloatProperty()
    must_be_returned = db.StringProperty(choices=['Yes', 'No'], default='No')
    picture = db.BlobProperty()
    thumbnail = db.BlobProperty()
    supplier = db.ReferenceProperty(Supplier)
    supplier_part_number = db.StringProperty()
    url = db.URLProperty()
    last_editor = db.UserProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)
    supports_extra_name_on_order = db.BooleanProperty(default=False)

    def __unicode__(self):
        return self.description

    def VisibleSortableLabel(self, label):
        """Strips numeric prefixes used for sorting.

        Labels may have a digit prefix which is used for sorting, but
        should not be shown to users.
        """
        if not label:
            return ''
        parts = label.split()
        if len(parts) > 0 and parts[0].isdigit():
            return ' '.join(parts[1:])
        return label

    def VisibleName(self):        
        return self.VisibleSortableLabel(self.name)

    def VisibleOrderFormSection(self):        
        return self.VisibleSortableLabel(self.order_form_section)


class Order(BaseModel):
    """A Captain can make an Order for a list of Items."""
    site = db.ReferenceProperty(NewSite, required=True)
    order_sheet = db.ReferenceProperty(OrderSheet, required=True)
    program = db.StringProperty()
    sub_total = db.FloatProperty()
    sales_tax = db.FloatProperty()  # Deprecated
    grand_total = db.FloatProperty()  # Deprecated.  Use GrandTotal()
    notes = db.TextProperty()    
    state = db.StringProperty()
    actual_total = db.FloatProperty()  
    reconciliation_notes = db.TextProperty(default='')    
    invoice_date = db.DateTimeProperty()
    vendor = db.ReferenceProperty(Supplier)
    logistics_start = db.StringProperty()
    logistics_end = db.StringProperty()
    logistics_instructions = db.TextProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    created_by = db.UserProperty(auto_current_user_add=True)
    modified = db.DateTimeProperty(auto_now=True)
    last_editor = db.UserProperty(auto_current_user=True)

    def put(self, *a, **k):
        self.program = self.site.program
        super(BaseModel, self).put(*a, **k)        

    def __unicode__(self):
        return ' '.join((self.site.number, self.site.name, 
                         self.order_sheet.name, 
                         '%d items' % len(list(self.orderitem_set)), 
                         '$%0.2f' % self.GrandTotal()))
    
    def CanMakeChanges(self):
        return self.state in ('new', 'Received')

    def VisibleNotes(self):
        if self.notes is None:
            return ''
        return self.notes

    def EstimatedTotal(self):
        if self.sub_total is None:
            return 0.
        t = self.sub_total * (1. + SALES_TAX_RATE)
        return math.ceil(t * 100.) / 100.

    def GrandTotal(self):
        if self.state == 'Deleted':
            return 0.
        if self.actual_total is not None:
            return self.actual_total
        else:
            return self.EstimatedTotal()

    def Total(self):
        return self.GrandTotal()
    
    def SalesTax(self):
        if self.state == 'Deleted':
            return 0.
        if self.sub_total is None:
            return 0.
        return self.sub_total * SALES_TAX_RATE

    # TODO: seems incorrect to update fulfilled orders.
    def UpdateSubTotal(self):
        """Recomputes sub_total by summing the cost of items and adding tax."""
        sub_total = 0.
        order_items = OrderItem.all().filter('order = ', self)
        for oi in order_items:
            quantity = oi.FloatQuantity()
            if oi.item.unit_cost is not None and quantity:
                sub_total += quantity * oi.item.unit_cost 
        if self.sub_total != sub_total:
            self.sub_total = sub_total
            self.put()
            logging.info('Updated subtotal for order %d to %0.2f', 
                         self.key().id(), sub_total)

    def LogisticsStart(self):
        for od in self.orderdelivery_set:
            return "%s (Delivery)" % od.delivery.delivery_date
        for od in self.orderpickup_set:
            return "%s (Pickup)" % od.pickup.pickup_date
        for od in self.orderretrieval_set:
            return "%s (Drop-off)" % od.retrieval.dropoff_date
        return None

    def LogisticsEnd(self):
        for od in self.orderretrieval_set:
            return "%s (Retrieval)" % od.retrieval.retrieval_date
        return None

    def LogisticsInstructions(self):
        for od in self.orderdelivery_set:
            return "%s%s %s%s %s" % (
                od.delivery.contact and 'Contact ' or '',
                od.delivery.contact or '',
                od.delivery.contact_phone and 'at ' or '',
                od.delivery.contact_phone or '',
                od.delivery.notes or '')

        for od in self.orderpickup_set:
            return "%s%s %s%s %s" % (
                od.pickup.contact and 'Contact ' or '',
                od.pickup.contact or '',
                od.pickup.contact_phone and 'at ' or '',
                od.pickup.contact_phone or '',
                od.pickup.notes or '')

        for od in self.orderretrieval_set:
            return "%s%s %s%s %s" % (
                od.retrieval.contact and 'Contact ' or '',
                od.retrieval.contact or '',
                od.retrieval.contact_phone and 'at ' or '',
                od.retrieval.contact_phone or '',
                od.retrieval.notes or '')
        return ''

    def UpdateLogistics(self):
        self.logistics_start = self.LogisticsStart()
        self.logistics_end = self.LogisticsEnd()
        self.logistics_instructions = self.LogisticsInstructions()
        self.put()


class OrderItem(BaseModel):
    """The Items that are in a given Order."""
    item = db.ReferenceProperty(Item)
    order = db.ReferenceProperty(Order)
    supplier = db.ReferenceProperty(Supplier)
    quantity = db.IntegerProperty(default=0)
    quantity_float = db.FloatProperty(default=0.0)
    name = db.StringProperty(default="")

    def FloatQuantity(self):
        """Returns quantity as a float."""
        if self.quantity:
            return float(self.quantity)
        elif self.quantity_float:
            return self.quantity_float
        else:
            return 0.0
            
    def IsEmpty(self):
        quantity = self.FloatQuantity()
        return not quantity and not self.name

    def SupportsName(self):
        return (self.item.supports_extra_name_on_order 
                or self.order.order_sheet.supports_extra_name_on_order)

    def VisibleQuantity(self):
        quantity = self.FloatQuantity()
        if quantity:
            if quantity % 1 == 0:
                return str(int(quantity))
            else:
                return str(quantity)
        else:
            return ''

    def VisibleCost(self):
        quantity = self.FloatQuantity()
        if quantity and not self.item.unit_cost:
            return '0'
        if quantity and self.item.unit_cost:
            return '%.2f' % (quantity * self.item.unit_cost)
        else:
            return ''


class Delivery(BaseModel):
    """Delivery to a site (no retrieval)."""
    site = db.ReferenceProperty(NewSite, required=True)
    delivery_date = db.StringProperty()
    delivery_date.verbose_name = 'Delivery Date (Mon-Fri only)'
    contact = db.StringProperty()
    contact.verbose_name = "Contact person (who will accept delivery)"
    contact_phone = db.StringProperty()    
    notes = db.TextProperty()
    notes.verbose_name = (
        'Instructions for delivery person')
    

class OrderDelivery(BaseModel):
    """Maps Order to Delivery."""
    order = db.ReferenceProperty(Order, required=True)
    delivery = db.ReferenceProperty(Delivery, required=True)


class Pickup(BaseModel):
    """Pick up from RTP warehouse."""
    site = db.ReferenceProperty(NewSite, required=True)
    pickup_date = db.StringProperty()
    pickup_date.verbose_name = 'Pickup Date (Mon-Fri only)'
    return_date = db.StringProperty()
    return_date.verbose_name = '(Optional) Return date for durable equipment'
    contact = db.StringProperty()
    contact.verbose_name = "Contact person (who will pick up)"
    contact_phone = db.StringProperty()    
    notes = db.TextProperty()
    notes.verbose_name = (
        'Instructions for warehouse staff')


class OrderPickup(BaseModel):
    """Maps Order to Pickup."""
    order = db.ReferenceProperty(Order, required=True)
    pickup = db.ReferenceProperty(Pickup, required=True)


class Retrieval(BaseModel):
    """Delivery and retrieval to and from a site."""
    site = db.ReferenceProperty(NewSite, required=True)
    dropoff_date = db.StringProperty()
    dropoff_date.verbose_name = 'Delivery Date (Mon-Fri only)'
    retrieval_date = db.StringProperty()
    retrieval_date.verbose_name = 'Retrieval Date (Mon-Fri only)'
    contact = db.StringProperty()
    contact.verbose_name = "Contact person (who will accept delivery)"
    contact_phone = db.StringProperty()    
    notes = db.TextProperty()
    notes.verbose_name = (
        'Instructions for delivery person')


class OrderRetrieval(BaseModel):
    """Maps Order to Retrieval."""
    order = db.ReferenceProperty(Order, required=True)
    retrieval = db.ReferenceProperty(Retrieval, required=True)


class InventoryItem(BaseModel):
    """The Items that are in the inventory."""
    item = db.ReferenceProperty(Item)
    quantity = db.IntegerProperty(default=0)
    quantity_float = db.FloatProperty(default=0.0)
    location = db.StringProperty()
    available_on = db.DateProperty()
    last_editor = db.UserProperty()
    modified = db.DateTimeProperty(auto_now=True)
    

class CheckRequest(BaseModel):
    """A Check Request is a request for reimbursement."""
    site = db.ReferenceProperty(NewSite)
    captain = db.ReferenceProperty(Captain)
    program = db.StringProperty()
    payment_date = db.DateProperty()
    labor_amount = db.FloatProperty(default=0.0)
    labor_amount.verbose_name = 'Labor Amount ($)'
    materials_amount = db.FloatProperty(default=0.0)
    materials_amount.verbose_name = 'Materials Amount ($)'
    food_amount = db.FloatProperty(default=0.0)
    food_amount.verbose_name = 'Food Amount ($)'
    description = db.TextProperty()
    name = db.StringProperty()
    name.verbose_name = 'Payable To'
    address = db.TextProperty()
    address.verbose_name = "Payee Address"
    tax_id = db.StringProperty()
    tax_id.verbose_name = "Payee Tax ID"
    tax_id.help_text = ("we'll notify you if we still need this information "
                        "to process the check")
    form_of_business = db.StringProperty(
        choices=('Corporation', 'Partnership', 'Sole Proprietor', 
                 'Don\'t Know'))
    form_of_business.verbose_name = "Payee Business Type"
    state = db.StringProperty(
        choices=('new', 'submitted', 'payable', 'fulfilled', 'deleted'), 
        default='new')
    last_editor = db.UserProperty()
    modified = db.DateTimeProperty(auto_now=True)

    def put(self, *a, **k):
        self.program = self.site.program
        super(BaseModel, self).put(*a, **k)        

    def Total(self):
        return self.labor_amount + self.materials_amount + self.food_amount
    

class VendorReceipt(BaseModel):
    """A Vendor Receipt is a report of a purchase outside of ROOMS."""
    site = db.ReferenceProperty(NewSite)
    captain = db.ReferenceProperty(Captain)
    program = db.StringProperty()
    purchase_date = db.DateProperty()
    vendor = db.StringProperty()
    supplier = db.ReferenceProperty(Supplier)
    amount = db.FloatProperty()
    amount.verbose_name = 'Purchase Amount ($)'
    description = db.TextProperty()
    state = db.StringProperty(
        choices=('new', 'submitted', 'payable', 'fulfilled', 'deleted'), 
        default='new')
    last_editor = db.UserProperty()
    modified = db.DateTimeProperty(auto_now=True)

    @property 
    def name(self):
        if self.supplier:
            return self.supplier.name
        return self.vendor

    def put(self, *a, **k):
        self.program = self.site.program
        super(BaseModel, self).put(*a, **k)        

    def Total(self):
        return self.amount or 0


class InKindDonation(BaseModel):
    """An In-kind donation to a site."""
    site = db.ReferenceProperty(NewSite)
    captain = db.ReferenceProperty(Captain)
    program = db.StringProperty()
    donation_date = db.DateProperty()
    donor = db.StringProperty()
    donor_phone = db.StringProperty()
    donor_info = db.TextProperty()
    donor_info.verbose_name = (
        'Include as much of the following donor information as possible:'
        ' donor name, company, address, phone, email.')
    labor_amount = db.FloatProperty(default=0.0)
    labor_amount.verbose_name = 'Labor Value ($)'
    materials_amount = db.FloatProperty(default=0.0)
    materials_amount.verbose_name = 'Materials Value ($)'
    description = db.TextProperty()
    budget = db.StringProperty(choices=('Normal', 'Roofing'), default='Normal')
    state = db.StringProperty(
        choices=('new', 'submitted', 'pending letter', 'fulfilled', 'deleted'), 
        default='new')
    last_editor = db.UserProperty()
    modified = db.DateTimeProperty(auto_now=True)
    
    @property 
    def name(self):
        return self.donor

    def put(self, *a, **k):
        self.program = self.site.program
        super(BaseModel, self).put(*a, **k)        

    def Total(self):
        return self.labor_amount + self.materials_amount

class Expense(BaseModel):
    """A generic expense."""
    payee = db.ReferenceProperty(Supplier)
    action = db.StringProperty(choices=('on account', 'need reimbursement'))

    site = db.ReferenceProperty(NewSite)
    captain = db.ReferenceProperty(Captain)
    program = db.StringProperty()
    date = db.DateProperty()
    amount = db.FloatProperty()
    amount.verbose_name = 'Purchase Amount ($)'
    description = db.TextProperty()
    state = db.StringProperty(
        choices=('new', 'submitted', 'payable', 'fulfilled', 'deleted'), 
        default='new')
    last_editor = db.UserProperty()
    modified = db.DateTimeProperty(auto_now=True)
