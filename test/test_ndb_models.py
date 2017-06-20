"""Unit tests for ndb_models."""

import unittest2
from room import ndb_models
import test_models


class ModelsTest(unittest2.TestCase):
    def setUp(self):
        test_models.CreateAll()

    def testOrder(self):
        o = test_models.KEYS['ORDER'].get()
        self.assertTrue(o)
        self.assertTrue(o.site)
        self.assertTrue(o.site.get())
        self.assertTrue(o.order_sheet)
        self.assertTrue(o.order_sheet.get())
        self.assertTrue(o.program)
        self.assertEquals(o.program, o.site.get().program)

    def testOrderUnicode(self):
        o = test_models.KEYS['ORDER'].get()
        self.assertEquals(u'110TEST Fixme Center Some Supplies 1 items $10.11', unicode(o))
    
    def testSiteBudget(self):
        mdl = test_models.KEYS['SITE'].get()
        self.assertEquals('$4818.88 unspent budget', mdl.BudgetStatement())
