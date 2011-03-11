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


class CaptainForm(djangoforms.ModelForm):
    class Meta:
        model = models.Captain
        exclude = ['modified', 'modified_by']


class CaptainContactForm(djangoforms.ModelForm):
    class Meta:
         model = models.Captain
         exclude = ['name', 'email', 'modified', 'modified_by', 'last_welcome']


class SiteForm(djangoforms.ModelForm):
    work_start = DateField('Work Start Date')
    work_end = DateField('Work End Date')
    number = forms.CharField(
        max_length=100,
        help_text = '"10001DAL" reads: 2010, #001, Daly City')
    class Meta:
         model = models.Site


class NewSiteForm(djangoforms.ModelForm):
    number = forms.CharField(
        max_length=100,
        help_text = '"10001DAL" reads: 2010, #001, Daly City')
    class Meta:
         model = models.NewSite


class CaptainSiteForm(djangoforms.ModelForm):
    work_start = DateField('Work Start Date')
    work_end = DateField('Work End Date')
    class Meta:
         model = models.Site
         exclude = ['number', 'name', 'street', 'applicant', 'sponsors', 
                    'postal_address']


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
    class Meta:
        model = models.Order
        exclude = ['created', 'created_by', 'modified', 'modified_by',
                   'order_sheet', 
                   'sub_total', 'sales_tax', 'grand_total', 'state',
                   'return_on'
                   ]


class CaptainOrderForm(djangoforms.ModelForm):
    pickup_on = DateField('Pickup On')
    return_on = DateField('Return On')

    class Meta:
        model = models.Order
        exclude = ['last_editor', 'created', 'modified', 'order_sheet', 
                   'sub_total', 'sales_tax', 'grand_total', 'state', 'captain']


class NewOrderForm(djangoforms.ModelForm):    
    site = djangoforms.ModelChoiceField(
        models.Site, widget=forms.HiddenInput)
    order_sheet = djangoforms.ModelChoiceField(
        models.OrderSheet, query=models.OrderSheet.all().order('name'))
    class Meta:
        model = models.Order
        fields = ['site', 'order_sheet']


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
    site = djangoforms.ModelChoiceField(
        models.Site, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(SiteExpenseForm, self).__init__(*args, **kwargs)
        entity = kwargs.get('instance')
        if entity:
            site = entity.site
            captains = [(sc.captain.key(), sc.captain.name) 
                        for sc in site.sitecaptain_set]
            captains.sort()
            if len(captains) > 1:
                captains.insert(0, ('', '----------'))
            self.fields['captain'] = djangoforms.ModelChoiceField(
                models.SiteCaptain,
                choices=captains)


class CheckRequestForm(SiteExpenseForm):
    payment_date = forms.DateField(required=True)
    name = forms.CharField(required=True, label='Payable To')
    description = forms.CharField(required=True, widget=forms.Textarea)
    class Meta:
        model = models.CheckRequest
        exclude = ['last_editor', 'modified', 'state']
    
class CheckRequestCaptainForm(CheckRequestForm):
    captain = djangoforms.ModelChoiceField(
        models.Captain, widget=forms.HiddenInput)


class VendorReceiptForm(SiteExpenseForm):
    purchase_date = forms.DateField(required=True)
    vendor = forms.ChoiceField(choices=[(v, v) for v in VENDOR_SELECTIONS],
                               required=True)
    amount = forms.FloatField(required=True)
    class Meta:
        model = models.VendorReceipt
        exclude = ['last_editor', 'modified', 'state']

class VendorReceiptCaptainForm(VendorReceiptForm):
    captain = djangoforms.ModelChoiceField(
        models.Captain, widget=forms.HiddenInput)


class InKindDonationForm(SiteExpenseForm):
    donation_date = forms.DateField(required=True)
    donor = forms.CharField(required=True)
    donor_phone = forms.CharField(required=True)
    description = forms.CharField(required=True, widget=forms.Textarea)
    class Meta:
        model = models.InKindDonation
        exclude = ['last_editor', 'modified', 'state']

class InKindDonationCaptainForm(InKindDonationForm):
    captain = djangoforms.ModelChoiceField(
        models.Captain, widget=forms.HiddenInput)
