'''
Tests for order module.
'''

import cStringIO
import unittest

from room import models 
from room import order 



class SomeOrdersTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.os = models.OrderSheet()
        self.os.put()
        self.os_id = self.os.key().id()
        self.s = models.Supplier(email='bob@supplier.com')
        self.s.put()
        self.i = models.Item(name='test item', supplier=self.s, 
                             unit_cost=50.,
                             appears_on_order_form=self.os)
        self.i.put()
        self.i_id = self.i.key().id()
        self.osi = models.OrderSheetItem(item=self.i, order_sheet=self.os)
        self.osi.put()
        self.site = models.NewSite(number='1234')
        self.site.put()
        self.site_id = self.site.key().id()
        self.order = models.Order(order_sheet=self.os, site=self.site)
        self.order.put()
        self.order_id = self.order.key().id()

    def tearDown(self):
        self.os.delete()
        self.s.delete()
        self.i.delete()
        self.osi.delete()
        self.site.delete()
        self.order.delete()
        unittest.TestCase.tearDown(self)

    def testOrderListInternal(self):
        d = order._OrderListInternal(self.os_id, 'unused')
        self.assertEquals(d['order_export_checkbox_prefix'], 'order_export_')
        self.assertEquals(d['order_sheet'], self.os)
        self.assertEquals(d['orders'], [self.order])

    def testOrderFulfillInternalEmpty(self):
        d = order._OrderFulfillInternal(self.order_id, self.os_id)
        self.assertEquals(d['back_to_list_url'], 
                          '/room/order/list/%d' % self.os_id)
        self.assertEquals(d['confirm_url'], '/room/order/fulfillconfirm/%d/%d/' 
                          % (self.order_id, self.os_id))
        self.assertEquals(d['order_sheet'], self.os)
        self.assertEquals(d['order'], self.order)
        self.assertEquals(d['order_items'], [])

    def testOrderFulfillConfirmInternalEmpty(self):
        r = order._OrderFulfillConfirmInternal(self.order_id, None)
        self.assertEquals(r['Location'], '/room/order/list/')

    def testOrderFulfillConfirmInternalToList(self):
        r = order._OrderFulfillConfirmInternal(self.order_id, self.os_id)
        self.assertEquals(r['Location'], '/room/order/list/%d' % self.os_id)

    def testOrderFulfillConfirmInternalToSite(self):
        r = order._OrderFulfillConfirmInternal(self.order_id, self.site_id)
        self.assertEquals(r['Location'], '/room/site/list/%d/' % self.site_id)

    def testOrderExportInternal(self):
        writable = cStringIO.StringIO()
        order._OrderExportInternal(writable, 
                                   {'order_export_%d' % self.order_id: ''})
        csv = writable.getvalue()
        csv_lines = csv.splitlines()
        self.assertEquals(
            'Order ID,site.number,order_sheet.name,sub_total'
            ',delivery_date,delivery_contact,delivery_contact_phone'
            ',delivery_location,pickup_on,number_of_days,return_on,notes,state'
            ',created,created_by,modified,modified_by',
            csv_lines[0])
        self.assertTrue(csv_lines[1].startswith('%d,1234,,,,,,,,1,,,,'
                                                % self.order_id))
        self.assertEquals(
            ',No Items in this Order!!!',
            csv_lines[2])

    def testSortOrderItemsWithSections(self):
        item = models.Item(name='20 it')
        item.put()
        oi = models.OrderItem(order=self.order, item=item)
        oi.put()
        ois = [oi]
        order._SortOrderItemsWithSections(ois)
        self.assertEquals(oi, ois[0])
        self.assertFalse(hasattr(oi, 'first_in_section'))
        item2 = models.Item(name='10 it', order_form_section='sec')
        item2.put()
        oi2 = models.OrderItem(order=self.order, item=item2)
        oi2.put()
        ois = [oi, oi2]
        order._SortOrderItemsWithSections(ois)
        self.assertEquals(oi, ois[0])
        self.assertEquals(oi2, ois[1])
        self.assertTrue(oi2.first_in_section)
        
    class MockRequest(object):
        POST={}
        FILES={}
        
    def testOrderEditBadOrderId(self):
        request = self.MockRequest()
        request.POST = {
            'SUBMIT': 'Submit and proceed to fulfillment (Staff only)',
            }
        r, d = order._OrderEditInternal(request, {}, 99)
        self.assertTrue(isinstance(r, order.http.HttpResponseRedirect))
        o = list(order.models.Order.all())
        self.assertEquals(1, len(o))
        saved_o = o[0]
        self.assertEquals(0., saved_o.GrandTotal())

    def testOrderEditGoodOrderIdNewOrder(self):
        request = self.MockRequest()
        request.POST = {
            'submit': 'Start New Order',
            }
        request.FILES = {}
        r, d = order._OrderEditInternal(request, {}, self.order_id)
        self.assertEquals(d['order'], self.order)
        o = list(order.models.Order.all())
        self.assertEquals(1, len(o))
        saved_o = o[0]
        self.assertEquals(0., saved_o.GrandTotal())

    def testOrderEditGoodOrderIdFulfill(self):
        request = self.MockRequest()
        request.POST = {
            'submit': 'Submit and proceed to fulfillment (Staff only)',
            }
        request.FILES = {}
        r, d = order._OrderEditInternal(request, {}, self.order_id)
        self.assertTrue(isinstance(r, order.http.HttpResponseRedirect))
        self.assertEquals('/room/order/fulfill/%d/%d/' % 
                          (self.order_id, self.os_id),
                          r['Location'])
        o = list(order.models.Order.all())
        self.assertEquals(1, len(o))
        saved_o = o[0]
        self.assertEquals(0., saved_o.GrandTotal())

    def testOrderEditGoodOrderIdOther(self):
        request = self.MockRequest()
        request.POST = {
            'submit': 'Submit this order',
            }
        self.oi = models.OrderItem(order=self.order, item=self.i, 
                                   supplier=self.s, quantity=9)
        self.oi.put()
        request.POST['item_%s' % self.oi.key()] = '100'
        request.FILES = {}
        r, d = order._OrderEditInternal(request, {}, self.order_id)
        self.assertTrue(isinstance(r, order.http.HttpResponseRedirect))
        self.assertEquals('/room/site/list/%d/' % self.site_id, r['Location'])
        o = list(order.models.Order.all())
        self.assertEquals(1, len(o))
        saved_o = o[0]
        self.assertEquals(5462.5, saved_o.GrandTotal())
        oi = list(models.OrderItem.all().filter('order =', self.order.key()))
        self.assertEquals(1, len(oi))

    def testOrderNew(self):
        request = self.MockRequest()
        r = order.OrderNew(request, self.site_id, self.os.code)
        self.assertEquals(2, len(list(models.Order.all())))

    def testOrderView(self):
        request = self.MockRequest()
        r = order.OrderView(request, self.order_id)


if __name__ == "__main__":
    unittest.main()
