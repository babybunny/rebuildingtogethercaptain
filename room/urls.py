from django.conf.urls.defaults import *

urlpatterns = patterns('room.views',
    (r'^/$', 'GoHome'),
    (r'^$', 'GoHome'),
    (r'^help', 'Help'),
    (r'^fix_city', 'FixCity'),
    (r'^standard_kit', 'StandardKit'),
                       

    (r'^site/without_order/$', 'SitesWithoutOrder'),
    (r'^site/without_order/(\d+)/$', 'SitesWithoutOrder'),
    (r'^send_email/(\d+)/$$', 'SitesWithoutOrderSendEmail'),

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

    (r'^site$', 'SiteList'),
    (r'^site/jump$', 'SiteJump'),
    (r'^site/list/$', 'SiteList'),
    (r'^site/list/(\d+)/$', 'SiteView'),
    (r'^site/list/(\w+)/$', 'SiteListByNumber'),
    (r'^site/export$', 'SiteExport'),
    (r'^site/new$', 'SiteNew'),
    (r'^site/edit/(\d+)/$', 'SiteEdit'),

    (r'^captain$', 'CaptainList'),
    (r'^captain/list$', 'CaptainList'),
    (r'^captain/export$', 'CaptainExport'),
    (r'^captain/new$', 'CaptainNew'),
    (r'^captain/edit/(\d+)/$', 'CaptainEdit'),

    (r'^captain_home$', 'CaptainHome'),
    (r'^staff_home$', 'StaffHome'),
    (r'^scoreboard$', 'Scoreboard'),

    (r'^staff$', 'StaffList'),
    (r'^staff/list$', 'StaffList'),
    (r'^staff/new$', 'StaffNew'),
    (r'^staff/edit/(\d+)/$', 'StaffEdit'),

    (r'^supplier$', 'SupplierList'),
    (r'^supplier/list$', 'SupplierList'),
    (r'^supplier/new$', 'SupplierNew'),
    (r'^supplier/edit/(\d+)/$', 'SupplierEdit'),

    (r'^inventory$', 'Inventory'),

    (r'^checkrequest/list/$', 'CheckRequestList'),
    (r'^checkrequest/new/(\d+)/$', 'CheckRequestNew'),
    (r'^checkrequest/edit/(\d+)/$', 'CheckRequestEdit'),
    (r'^checkrequest/view/(\d+)/$', 'CheckRequestView'),

    (r'^vendorreceipt/list/$', 'VendorReceiptList'),
    (r'^vendorreceipt/new/(\d+)/$', 'VendorReceiptNew'),
    (r'^vendorreceipt/edit/(\d+)/$', 'VendorReceiptEdit'),
    (r'^vendorreceipt/view/(\d+)/$', 'VendorReceiptView'),
)

urlpatterns += patterns(
    'room.order',
    (r'^order$', 'OrderList'),
    (r'^order/preview/(\d+)/$', 'OrderPreview'),
    (r'^order/list/.?$', 'OrderList'),
    (r'^order/list/(\d+)$', 'OrderList'),
    (r'^order/export$', 'OrderExport'),
    (r'^order/new/(\d+)/$', 'OrderNew'),
    (r'^order/new/(\d+)/(\w+)/$', 'OrderNew'),
    (r'^order/edit/(\d+)/$', 'OrderEdit'),
    (r'^order/logistics/(\d+)/$', 'OrderLogistics'),
    (r'^order/view/(\d+)/$', 'OrderView'),
    (r'^order/fulfill/(\d+)/$', 'OrderFulfill'),
    (r'^order/fulfill/(\d+)/(\d+)/$', 'OrderFulfill'),
    (r'^order/fulfillconfirm/(\d+)/$', 'OrderFulfillConfirm'),
    (r'^order/fulfillconfirm/(\d+)/(\d+)/$', 'OrderFulfillConfirm'),
)
