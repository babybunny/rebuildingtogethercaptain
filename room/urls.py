from django.conf.urls.defaults import *

urlpatterns = patterns('room.views',
    (r'^/$', 'Welcome'),
    (r'^$', 'Welcome'),
    (r'^help', 'Help'),

    (r'^item$', 'ItemList'),
    (r'^item/list$', 'ItemList'),
    (r'^item/new$', 'ItemNew'),
    (r'^item/edit/(\d+)/$', 'ItemEdit'),
    (r'^item/picture/(\d+)/$', 'ItemPicture'),
    (r'^item/thumbnail/(\d+)/$', 'ItemThumbnail'),

    (r'^order_sheet$', 'OrderSheetList'),
    (r'^order_sheet/list$', 'OrderSheetList'),
    (r'^order_sheet/new$', 'OrderSheetNew'),
    (r'^order_sheet/edit/(\d+)/$', 'OrderSheetEdit'),
    (r'^order_sheet/itemdelete/(\w+)/$', 'OrderSheetItemDelete'),

    (r'^site$', 'SiteList'),
    (r'^site/jump$', 'SiteJump'),
    (r'^site/list$', 'SiteList'),
    (r'^site/list/(\d+)/$', 'SiteList'),
    (r'^site/list/(\w+)/$', 'SiteListByNumber'),
    (r'^site/new$', 'SiteNew'),
    (r'^site/edit/(\d+)/$', 'SiteEdit'),

    (r'^captain$', 'CaptainList'),
    (r'^captain/list$', 'CaptainList'),
    (r'^captain/new$', 'CaptainNew'),
    (r'^captain/edit/(\d+)/$', 'CaptainEdit'),

    (r'^captain_home$', 'CaptainHome'),
    (r'^staff_home$', 'StaffHome'),

    (r'^staff$', 'StaffList'),
    (r'^staff/list$', 'StaffList'),
    (r'^staff/new$', 'StaffNew'),
    (r'^staff/edit/(\d+)/$', 'StaffEdit'),

    (r'^supplier$', 'SupplierList'),
    (r'^supplier/list$', 'SupplierList'),
    (r'^supplier/new$', 'SupplierNew'),
    (r'^supplier/edit/(\d+)/$', 'SupplierEdit'),

    (r'^order$', 'OrderList'),
    (r'^order/list/.?$', 'OrderList'),
    (r'^order/list/(\d+)$', 'OrderList'),
    (r'^order/export$', 'OrderExport'),
    (r'^order/new/(\d+)/$', 'OrderNew'),
    (r'^order/new/(\w+)/(\w+)/$', 'OrderNew'),
    (r'^order/edit/(\d+)/$', 'OrderEdit'),

    (r'^inventory$', 'Inventory'),
)
