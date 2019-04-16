"""Unit tests for ndb_models."""
import unittest

import app_engine_test_utils
import test_models


class ModelsTest(unittest.TestCase):
  def setUp(self):
    app_engine_test_utils.activate_app_engine_testbed_and_clear_cache()

    self.keys = test_models.CreateAll()

  def tearDown(self):
    test_models.DeleteAll(self.keys)

  def testOrder(self):
    o = self.keys['ORDER'].get()
    self.assertTrue(o)
    self.assertTrue(o.site)
    self.assertTrue(o.site.get())
    self.assertTrue(o.order_sheet)
    self.assertTrue(o.order_sheet.get())
    self.assertTrue(o.program)
    self.assertEquals(o.program, o.site.get().program)

  def testOrderUnicode(self):
    o = self.keys['ORDER'].get()
    self.assertEquals(u'110TEST Fixme Center Some Supplies 3 items $10.92', unicode(o))

  def testOrder2Unicode(self):
    o = self.keys['ORDER2'].get()
    self.assertEquals(u'110TEST Fixme Center Some Supplies 1 items $21.10', unicode(o))

  def testSiteBudget(self):
    mdl = self.keys['SITE'].get()
    self.assertEquals('$4838.09 unspent budget', mdl.BudgetStatement())

  def testOrderInvoice(self):
    o = self.keys['ORDER3'].get()
    self.assertEquals(u'110TEST Fixme Center Safety Materials 0 items $0.00', unicode(o))
    self.assertIsNone(o.internal_invoice)
    o.SetInvoiceNumber()
    self.assertIsNotNone(o.internal_invoice)
    self.assertEquals(10000, o.internal_invoice.get().invoice_number)
    
  def testVendorReceipt(self):
    mdl = self.keys['VENDORRECEIPT'].get()
    self.assertEquals(None, mdl.amount)
