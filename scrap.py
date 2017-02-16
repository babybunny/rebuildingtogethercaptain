
from room.models import OrderItem
orders = OrderItem.all().filter('item = ', None).fetch(100)
print orders
for o in orders:
  o.delete()


from room import models
ois = models.OrderItem.all().fetch(1000)
for oi in ois:
  oi.delete()


from room import models
ors = models.OrderSheet.all().filter('code = ', 'RNT').get()
ois = models.Item.all().filter('appears_on_order_form = ', ors).fetch(1000)
for oi in ois:
  oi.delete()
