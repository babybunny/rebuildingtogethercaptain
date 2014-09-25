# Copyright 2011 Luke Stone

"""Django forms for models."""

# This don't work in appengine, we use djangoforms instead.
# from django.forms import ModelForm
from django import forms  # DateField, DateTimeInput
from google.appengine.ext.db import djangoforms
import common
import models

VENDOR_SELECTIONS = (    
    'Home Depot',
    'Kelly-Moore Paints',
    'Palo Alto Hardware',
    'Wisnom\'s ',
    'Ocean Shore Hardware',
    'AAA Rentals',
    'San Mateo Rentals',
    'Other (put name in Description)',
    )

def DateField(label):
    """Helper to produce data fields for forms."""
    return forms.DateField(
        label=label, required=False,  
        help_text='mm/dd/yyyy',
        widget=forms.DateTimeInput(attrs={'class':'input',
                                          'size':'10'
                                          },
                                   format='%m/%d/%Y'
                                   ))

def SortedCaptainChoiceField():
    return djangoforms.ModelChoiceField(
        models.Captain, 
        models.Captain.all().order('name'))

def SortedSiteChoiceField():
    return djangoforms.ModelChoiceField(
        models.NewSite, 
        models.NewSite.all().order('number'))


class CaptainForm(djangoforms.ModelForm):
    class Meta:
        model = models.Captain
        exclude = ['modified', 'last_editor', 'last_welcome', 'search_prefixes']


class CaptainContactForm(djangoforms.ModelForm):
    class Meta:
         model = models.Captain
         exclude = ['name', 'email', 'modified', 'last_editor', 'last_welcome',
                    'search_prefixes']


class NewSiteForm(djangoforms.ModelForm):
    number = forms.CharField(
        max_length=10,
        help_text = '"10001DAL" reads: 2010, #001, Daly City')
    street_number = forms.CharField(
        max_length=100,
        help_text = models.NewSite.street_number.help_text)
    city_state_zip = forms.CharField(
        max_length=100,
        help_text = models.NewSite.city_state_zip.help_text)
    jurisdiction_choice = djangoforms.ModelChoiceField(
        models.Jurisdiction, query=models.Jurisdiction.all().order('name'),
        label='Jurisdiction')
    class Meta:
         model = models.NewSite
         exclude = ['search_prefixes', 'program', 'jurisdiction', 'year']


class CaptainSiteForm(djangoforms.ModelForm):
    work_start = DateField('Work Start Date')
    work_end = DateField('Work End Date')
    class Meta:
        # TODO: is this the wrong model!??  should be NewSite?
        model = models.Site
        exclude = ['number', 'name', 'applicant', 'sponsors', 
                   'postal_address', 'search_prefixes']


class SiteCaptainSiteForm(djangoforms.ModelForm):
    captain = SortedCaptainChoiceField()
    class Meta:
        model = models.SiteCaptain
        exclude = ['site']


class StaffForm(djangoforms.ModelForm):
    since = DateField('Since')
    class Meta:
         model = models.Staff
         exclude = ['user', 'last_welcome']


class SupplierForm(djangoforms.ModelForm):
    since = DateField('Since')
    class Meta:
         model = models.Supplier
         exclude = ['user']

class SupplierFormSimple(djangoforms.ModelForm):
    class Meta:
         model = models.Supplier
         fields = ['name', 'address', 'phone']

class OrderSheetForm(djangoforms.ModelForm):
     class Meta:
         model = models.OrderSheet
         exclude = ['created']


class ItemForm(djangoforms.ModelForm):    
    class Meta:
        model = models.Item
        exclude = ['last_editor', 'created', 'modified', 'thumbnail']


class OrderForm(djangoforms.ModelForm):
    initial = {'pickup_on': common.NRD}
    site = SortedSiteChoiceField()
    class Meta:
        model = models.Order
        exclude = ['last_editor', 'created', 'created_by', 
                   'modified', 'order_sheet', 
                   'sub_total', 'sales_tax', 'grand_total', 'state', 
                   'program']


class CaptainOrderForm(djangoforms.ModelForm):
    pickup_on = DateField('Pickup On')
    return_on = DateField('Return On')

    class Meta:
        model = models.Order
        exclude = ['last_editor', 'created', 'created_by', 
                   'modified', 'order_sheet', 
                   'sub_total', 'sales_tax', 'grand_total', 'state', 
                   'captain', 'site', 'program']


class NewOrderForm(djangoforms.ModelForm):    
    site = djangoforms.ModelChoiceField(
        models.Site, widget=forms.HiddenInput)
    order_sheet = djangoforms.ModelChoiceField(
        models.OrderSheet, query=models.OrderSheet.all().order('name'))
    class Meta:
        model = models.Order
        fields = ['site', 'order_sheet', 'program']


class DeliveryForm(djangoforms.ModelForm):
     class Meta:
         model = models.Delivery
         exclude = ['site']


class PickupForm(djangoforms.ModelForm):
     class Meta:
         model = models.Pickup
         exclude = ['site']


class RetrievalForm(djangoforms.ModelForm):
     class Meta:
         model = models.Retrieval
         exclude = ['site']


class InventoryItemForm(djangoforms.ModelForm):
     class Meta:
         model = models.InventoryItem
         exclude = ['last_editor', 'modified', 'item']


class SiteExpenseForm(djangoforms.ModelForm):
    def __init__(self, *args, **kwargs):
        staff = kwargs.pop('staff')
        super(SiteExpenseForm, self).__init__(*args, **kwargs)
        if staff:
            self.fields['site'] = djangoforms.ModelChoiceField(
                models.NewSite, models.NewSite.all().order('number'))
            entity = kwargs.get('instance')
            if entity:
                site = entity.site
                captains = [(sc.captain.key(), sc.captain.name) 
                            for sc in site.sitecaptain_set]
                captains.sort()
                staff_captain = common.GetStaffCaptain()
                captains.append((staff_captain.key(), staff_captain.name))
                self.fields['captain'] = djangoforms.ModelChoiceField(
                    models.SiteCaptain,
                    choices=captains)

        else:
            self.fields['site'] = djangoforms.ModelChoiceField(
                models.NewSite, widget=forms.HiddenInput)
            self.fields['captain'] = djangoforms.ModelChoiceField(
                models.Captain, widget=forms.HiddenInput)



class CheckRequestForm(SiteExpenseForm):
    payment_date = forms.DateField(required=True)
    name = forms.CharField(required=True, label='Payable To')
    description = forms.CharField(
        required=True, widget=forms.Textarea,
        label=('Description '
            '(Please include place of purchase and list of items purchased '
            'and submit corresponding receipt.)')
        )
    class Meta:
        model = models.CheckRequest
        exclude = ['last_editor', 'modified', 'program']


class VendorReceiptForm(SiteExpenseForm):
    purchase_date = forms.DateField(required=True)
    
    supplier = djangoforms.ModelChoiceField(
        models.Supplier,
        query=models.Supplier.all().order('name'),
        label="Vendor",
        help_text="or add a new vendor using the form on the right")
    amount = forms.FloatField(required=True)
    class Meta:
        model = models.VendorReceipt
        exclude = ['last_editor', 'modified', 'program', 'vendor']


class InKindDonationForm(SiteExpenseForm):
    donation_date = forms.DateField(required=True)
    donor = forms.CharField(required=True)
    donor_phone = forms.CharField(required=True)
    description = forms.CharField(required=True, widget=forms.Textarea)
    class Meta:
        model = models.InKindDonation
        exclude = ['last_editor', 'modified', 'program']
        
