"""Scratch code for dealing with duplicate order items.

See https://github.com/babybunny/rebuildingtogethercaptain/issues/465

$ python /Users/babybunny/google-cloud-sdk/platform/google_appengine/remote_api_shell.py -s rebuildingtogethercaptain.appspot.com
App Engine remote_api shell
Python 2.7.9 (v2.7.9:648dcafa7e5f, Dec 10 2014, 10:10:46)
[GCC 4.2.1 (Apple Inc. build 5666) (dot 3)]
The db, ndb, users, urlfetch, and memcache modules are imported.
s~rebuildingtogethercaptain-hrd> from local import issue465
s~rebuildingtogethercaptain-hrd> issue465.find_dupes(2018, 1, 1)
"""

from collections import defaultdict
import datetime
import csv

from gae.room import ndb_models

CSV_FILENAME = 'issue465.csv'

oi_by_i = defaultdict(list)

def find_dupes(y, m, d):
    oq = ndb_models.Order.query(ndb_models.Order.created > datetime.datetime(y, m, d, 0, 0, 0))
    oqf = oq.fetch()
    # print oqf
    for o in oqf:
        print "processing {0!s}".format(o.key)
        oiq = ndb_models.OrderItem.query(ndb_models.OrderItem.order == o.key)
        for oi in oiq:
            k = (oi.order, oi.item)
            oi_by_i[k].append(oi.key)

    for ok_ik, oikl in sorted(oi_by_i.items()):
        if len(oikl) > 1:
            print "DUPLICATE!!"
            print ok_ik
            print oikl
        else:
            print "no duplicates for {0!s}".format(ok_ik)

    with open(CSV_FILENAME, 'wb') as outfile: 
        outcsv = csv.writer(outfile)
        for ok_ik, oikl in sorted(oi_by_i.items()):
            if len(oikl) > 1:
                for oik in sorted(oikl[:-1]):
                    outcsv.writerow([ok_ik[0].integer_id(), ok_ik[1].integer_id(), oik.integer_id()])

                
def del_dupes_from_csv():
    with open(CSV_FILENAME, 'r') as infile:
        csvreader = csv.reader(infile)
        for ok, ik, oik in csvreader:
            print ok, ik, oik
            k = ndb_models.ndb.Key(ndb_models.OrderItem, int(oik))
            print k
            k.delete()
            
