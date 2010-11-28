'''
Tests for order module.
'''

import cStringIO
import unittest

from room import models 
from room import order 



class SomeOrdersTest(unittest.TestCase):

    def setUp(self):
        self.os = models.OrderSheet()
        self.os.put()
        self.site = models.NewSite(number='1234')
        self.site.put()
        self.order = models.Order(order_sheet=self.os, site=self.site)
        self.order.put()

    def tearDown(self):
        self.os.delete()
        self.site.delete()
        self.order.delete()

    def testOrderListInternal(self):
        d = order._OrderListInternal(1, 'unused')
        self.assertEquals(d['order_export_checkbox_prefix'], 'order_export_')
        self.assertEquals(d['order_sheet'], self.os)
        self.assertEquals(d['orders'], [self.order])

    def testOrderFulfillInternalEmpty(self):
        d = order._OrderFulfillInternal(3, 1)
        self.assertEquals(d['back_to_list_url'], '/room/order/list/1')
        self.assertEquals(d['confirm_url'], '/room/order/fulfillconfirm/3/1/')
        self.assertEquals(d['order_sheet'], self.os)
        self.assertEquals(d['order'], self.order)
        self.assertEquals(d['order_items'], [])

    def testOrderFulfillConfirmInternalEmpty(self):
        r = order._OrderFulfillConfirmInternal(3, None)
        self.assertEquals(r['Location'], '/room/order/list/')

    def testOrderFulfillConfirmInternalToList(self):
        r = order._OrderFulfillConfirmInternal(3, 1)
        self.assertEquals(r['Location'], '/room/order/list/1')

    def testOrderFulfillConfirmInternalToSite(self):
        r = order._OrderFulfillConfirmInternal(3, 2)
        self.assertEquals(r['Location'], '/room/site/list/2/')

    def testOrderExportInternal(self):
        writable = cStringIO.StringIO()
        order._OrderExportInternal(writable, {'order_export_3': ''})
        csv = writable.getvalue()
        csv_lines = csv.splitlines()
        self.assertEquals(
            'Order ID,site.number,order_sheet.name,sub_total,sales_tax'
            ',grand_total,delivery_date,delivery_contact,delivery_contact_phone'
            ',delivery_location,pickup_on,number_of_days,return_on,notes,state'
            ',created,created_by,modified,modified_by',
            csv_lines[0])
        self.assertTrue(csv_lines[1].startswith('3,1234,,,,,,,,,,1,,,,'))
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
        

if __name__ == "__main__":
    unittest.main()
