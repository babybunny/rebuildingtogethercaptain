'''
Tests for 
'''
import unittest

from room import models 

class Test(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.captain = models.Captain(email='1234')
        self.captain.put()
        self.os = models.OrderSheet()
        self.os.put()
        self.site = models.NewSite(number='1234')
        self.site.put()
        self.order = models.Order(order_sheet=self.os, site=self.site)
        self.order.put()
        self.item = models.Item(name='foo', unit_cost=2.4)
        self.item.put()
        self.oi = models.OrderItem(order=self.order, 
                                   item=self.item, quantity=2)
        self.oi.put()
        self.item2 = models.Item(name='foo2', unit_cost=0.3)
        self.item2.put()
        self.oi2 = models.OrderItem(order=self.order, 
                                    item=self.item2, quantity=0)
        self.oi2.put()

    def tearDown(self):
        self.captain.delete()
        self.os.delete()
        self.site.delete()
        self.order.delete()
        self.item.delete()
        self.oi.delete()
        self.item2.delete()
        self.oi2.delete()
        unittest.TestCase.tearDown(self)

    def testModels(self):
        self.assertTrue(models)

    def testCaptain(self):
        self.assertTrue(models.Captain(email='luke'))

    def testSite(self):
        self.assertTrue(models.Site(number='1234'))

    def testNewSite(self):
        site = models.NewSite(number='1234', name='Belle Haven',
                              street='Main Street', 
                              street_number='100 Main Street',
                              city_state_zip='Menlo Park CA 94025', budget=1000)
        self.assertTrue(site)
        self.assertTrue(site.put())
        cr = models.CheckRequest(site=site, labor_amount=450.)
        cr.put()
        try:
            self.assertEquals('Site #%d | Belle Haven' % site.key().id(), 
                              site.__unicode__())
            self.assertEquals('100 Main Street, Menlo Park CA 94025', 
                              site.StreetAddress())
            self.assertEquals(250, site.StandardKitCost())        
            self.assertEquals(250, site.OrderTotal())
            self.assertEquals(450, site.CheckRequestTotal())
            self.assertEquals(300, site.BudgetRemaining())
            self.assertEquals([], list(site.VisibleOrders()))
        finally:
            site.delete()
            cr.delete()

    def testSiteCaptain(self):
        self.assertTrue(models.SiteCaptain(site=self.site, 
                                           captain=self.captain))

    def testStaff(self):
        self.assertTrue(models.Staff(email='foo'))

    def testSupplier(self):
        self.assertTrue(models.Supplier(email='foo'))

    def testOrderSheet(self):
        self.assertTrue(models.OrderSheet())

    def testItem(self):
        item = models.Item(name='10 foo', order_form_section='20 top')
        self.assertTrue(item)
        self.assertEquals('foo', item.VisibleName())
        self.assertEquals('top', item.VisibleOrderFormSection())

    def testOrder(self):
        self.assertTrue(self.order)
        self.assertFalse(self.order.CanMakeChanges())
        self.assertEquals('', self.order.VisibleNotes())
        self.assertEquals(0., self.order.GrandTotal())        

    def testOrderUpdateSubTotal(self):
        self.assertEquals(None, self.order.sub_total)  
        self.order.UpdateSubTotal()
        self.assertEquals(4.8, self.order.sub_total)

    def testOrderItem(self):
        self.assertTrue(self.oi)
        self.assertEquals(2, self.oi.VisibleQuantity())
        self.assertEquals('4.80', self.oi.VisibleCost())

    def testInventoryItem(self):
        ii = models.InventoryItem(item=self.item)
        try:
            ii.put()
            self.assertTrue(ii)
        finally:
            ii.delete()

    def testCheckRequest(self):
        cr = models.CheckRequest()
        try:
            cr.put()
            self.assertTrue(cr)
        finally:
            cr.delete()


if __name__ == "__main__":
    unittest.main()
