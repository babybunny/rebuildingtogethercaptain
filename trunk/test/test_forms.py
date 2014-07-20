'''
Tests for 
'''
import unittest

from room import forms 

class Test(unittest.TestCase):

    def testDateField(self):
        self.assertTrue(forms.DateField('label'))
        
    def testCaptainForm(self):
        self.assertTrue(forms.CaptainForm())

    def testCaptainContactForm(self):
        self.assertTrue(forms.CaptainContactForm())

    def testNewSiteForm(self):
        self.assertTrue(forms.NewSiteForm())

    def testCaptainSiteForm(self):
        self.assertTrue(forms.CaptainSiteForm())

    def testSiteCaptainSiteForm(self):
        self.assertTrue(forms.SiteCaptainSiteForm())

    def testStaffForm(self):
        self.assertTrue(forms.StaffForm())

    def testSupplierForm(self):
        self.assertTrue(forms.SupplierForm())

    def testOrderSheetForm(self):
        self.assertTrue(forms.OrderSheetForm())

    def testItemForm(self):
        self.assertTrue(forms.ItemForm())

    def testOrderForm(self):
        self.assertTrue(forms.OrderForm())

    def testNewOrderForm(self):
        self.assertTrue(forms.NewOrderForm())

    def testCaptainOrderForm(self):
        self.assertTrue(forms.CaptainOrderForm())

    def testInventoryItemForm(self):
        self.assertTrue(forms.InventoryItemForm())

    def testCheckRequestForm(self):
        self.assertTrue(forms.CheckRequestForm())


if __name__ == "__main__":
    unittest.main()
