"""Unit tests for ndb_models."""

import unittest2
from room import ndb_models
import test_models


class ModelsTest(unittest2.TestCase):
    def setUp(self):
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
        self.assertEquals(u'110TEST Fixme Center Some Supplies 2 items $10.92', unicode(o))
    
    def testOrder2Unicode(self):
        o = self.keys['ORDER2'].get()
        self.assertEquals(u'110TEST Fixme Center Some Supplies 0 items $9.10', unicode(o))

    def testSiteBudget(self):
        mdl = self.keys['SITE'].get()
        self.assertEquals('$4838.09 unspent budget', mdl.BudgetStatement())
