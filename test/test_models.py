'''
Tests for 
'''
import unittest

from room import models 

class Test(unittest.TestCase):

    def testModels(self):
        self.assertTrue(models)

    def testDateField(self):
        self.assertTrue(models.DateField('label'))
        
    def testCaptain(self):
        self.assertTrue(models.Captain(email='luke'))

    def testCaptainForm(self):
        self.assertTrue(models.CaptainForm())

    def testCaptainContactForm(self):
        self.assertTrue(models.CaptainContactForm())

    def testSite(self):
        self.assertTrue(models.Site(number='1234'))

    def testNewSite(self):
        site = models.NewSite(number='1234', name='Belle Haven',
                              street='Main Street', street_number='100',
                              city_state_zip='Menlo Park CA 94025', budget=1000)
        self.assertTrue(site)
        self.assertTrue(site.put())
        self.assertEquals('Site #1 | Belle Haven', 
                          site.__unicode__())
        self.assertEquals('100 Main Street, Menlo Park CA 94025', 
                          site.StreetAddress())
        self.assertEquals(250, site.StandardKitCost())        
        self.assertEquals(250, site.OrderTotal())
        self.assertEquals(750, site.BudgetRemaining())
        self.assertEquals([], list(site.VisibleOrders()))

    def testSiteForm(self):
        self.assertTrue(models.SiteForm())

    def testNewSiteForm(self):
        self.assertTrue(models.NewSiteForm())

    def testCaptainSiteForm(self):
        self.assertTrue(models.CaptainSiteForm())

    def testSiteCaptain(self):
        site = models.NewSite(number='1234').put()
        captain = models.Captain(email='1234').put()
        self.assertTrue(models.SiteCaptain(site=site, captain=captain))

    def testSiteCaptainSiteForm(self):
        self.assertTrue(models.SiteCaptainSiteForm())

    def testStaff(self):
        self.assertTrue(models.Staff(email='foo'))

    def testStaffForm(self):
        self.assertTrue(models.StaffForm())

    def testSupplier(self):
        self.assertTrue(models.Supplier(email='foo'))

    def testSupplierForm(self):
        self.assertTrue(models.SupplierForm())

    def testOrderSheet(self):
        self.assertTrue(models.OrderSheet())

    def testOrderSheetForm(self):
        self.assertTrue(models.OrderSheetForm())

    def testItem(self):
        item = models.Item(name='10 foo', order_form_section='20 top')
        self.assertTrue(item)
        self.assertEquals('foo', item.VisibleName())
        self.assertEquals('top', item.VisibleOrderFormSection())

    def testItemForm(self):
        self.assertTrue(models.ItemForm())

    def testOrderSheetItem(self):
        item = models.Item(name='10 foo', order_form_section='20 top').put()
        os = models.OrderSheet().put()
        self.assertTrue(models.OrderSheetItem(order_sheet=os, item=item))

    def testOrder(self):
        os = models.OrderSheet().put()
        site = models.NewSite(number='1234').put()
        order = models.Order(order_sheet=os, site=site)
        order.put()
        self.assertTrue(order)
        self.assertFalse(order.CanMakeChanges())
        self.assertEquals('', order.VisibleNotes())

    def testOrderForm(self):
        self.assertTrue(models.OrderForm())

    def testNewOrderForm(self):
        self.assertTrue(models.NewOrderForm())

    def testCaptainOrderForm(self):
        self.assertTrue(models.CaptainOrderForm())

    def testOrderItem(self):
        os = models.OrderSheet().put()
        site = models.NewSite(number='1234').put()
        o = models.Order(order_sheet=os, site=site)
        o.put()
        item = models.Item(name='foo').put()
        s = models.Supplier(email='1234').put()
        oi = models.OrderItem(order=o, item=item, supplier=s, quantity=1)
        oi.put()
        self.assertTrue(oi)
        self.assertEquals(1, oi.VisibleQuantity())
        self.assertEquals('', oi.VisibleCost())

    def testInventoryItem(self):
        item = models.Item(name='foo').put()
        ii = models.InventoryItem(item=item)
        ii.put()
        self.assertTrue(ii)

    def testInventoryItemForm(self):
        self.assertTrue(models.InventoryItemForm())


if __name__ == "__main__":
    unittest.main()
