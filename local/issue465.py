"""Scratch code for dealing with duplicate order items.

See https://github.com/babybunny/rebuildingtogethercaptain/issues/465
"""

from collections import defaultdict
import datetime

from gae.room import ndb_models

def find_dupes(y, m, d):
    oq = ndb_models.Order.query(ndb_models.Order.created > datetime.datetime(y, m, d, 0, 0, 0))
    oqf = oq.fetch(5)
    # print oqf
    oi_by_i = defaultdict(list)
    for o in oqf:
        # print o
        oiq = ndb_models.OrderItem.query(ndb_models.OrderItem.order == o.key)
        for oi in oiq:
            k = (oi.order, oi.item)
            oi_by_i[k].append(oi.key)

    for ok_ik, oikl in oi_by_i.iteritems(): 
        if len(oikl) > 1:
            print "DUPLICATE!!"
            print ok_ik
            print oikl
        else:
            print "no duplicates for {0!s}".format(ok_ik)
