from django.conf.urls.defaults import *

urlpatterns = patterns(
    'room.staff',
    (r'^/$', 'GoHome'),
    (r'^$', 'GoHome'),
    (r'^staff_home$', 'StaffHome'),
    (r'^select_program$', 'SelectProgram'),
    (r'^select_program/(.+)/$', 'SelectProgram'),
    (r'^site/jump$', 'SiteJump'),
    (r'^site/without_order/$', 'SitesWithoutOrder'),
    (r'^site/without_order/(\d+)/$', 'SitesWithoutOrder'),
    (r'^send_email/(\d+)/$$', 'SitesWithoutOrderSendEmail'),
    (r'^admin/put_suppliers', 'PutSuppliers'),
    (r'^admin/fix_city', 'FixCity'),
    (r'^admin/fix_last_editor', 'FixLastEditor'),
    (r'^admin/add_standard_kit_order/(\w+)/$', 'AddStandardKitOrder'),
    (r'^admin/search_prefix', 'RecomputeSearchPrefixes'),
    (r'^admin/order_logistics', 'RecomputeOrderLogistics'),
    (r'^admin/delete_empty_order_items', 'DeleteEmptyOrderItems'),
    (r'^admin/fix_program$', 'FixProgramFromNumber'),
    (r'^admin/fix_program/(.+)/$', 'FixProgramFromNumber'),
    (r'^admin/recompute_orders$', 'RecomputeOrders'),
    )

urlpatterns += patterns(
    'room.scoreboard',
    (r'^all_programs_scoreboard$', 'AllProgramsScoreboard'),
    (r'^scoreboard$', 'Scoreboard'),
    (r'^scoreboard/orders$', 'ScoreboardOrders'),
    (r'^scoreboard/captains$', 'ScoreboardCaptains'),
    (r'^scoreboard/staff$', 'ScoreboardStaff'),
    )

urlpatterns += patterns(
    'room.views',
    (r'^help', 'Help'),
    (r'^standard_kit', 'StandardKit'),
                       
    (r'^item$', 'ItemList'),
    (r'^item/list$', 'ItemList'),
    (r'^item/new$', 'ItemNew'),
    (r'^item/edit/(\d+)/$', 'ItemEdit'),
    (r'^item/price/(\d+)/$', 'ItemPrice'),
    (r'^item/picture/(\d+)/$', 'ItemPicture'),
    (r'^item/thumbnail/(\d+)/$', 'ItemThumbnail'),

    (r'^order_sheet$', 'OrderSheetList'),
    (r'^order_sheet/list$', 'OrderSheetList'),
    (r'^order_sheet/new$', 'OrderSheetNew'),
    (r'^order_sheet/edit/(\d+)/$', 'OrderSheetEdit'),
    (r'^order_sheet/item_list/(\d+)/$', 'OrderSheetItemList'),

    (r'^site$', 'SiteList'),
    (r'^site/list/$', 'SiteList'),
    (r'^site/debug/$', 'SiteListDebug'),
    (r'^site/list/(\d+)/$', 'SiteView'),
    (r'^site/list/(\w+)/$', 'SiteListByNumber'),
    (r'^site/expenses/(\d+)/$', 'SiteExpenses'),
    (r'^site/summary/(\d+)/$', 'SiteSummary'),
    (r'^site/budget/$', 'SiteBudget'),
    (r'^site/budget_export/$', 'SiteBudgetExport'),
    (r'^site/autocomplete/$', 'SiteAutocomplete'),
    (r'^site/export$', 'SiteExport'),
    (r'^site/new$', 'SiteNew'),
    (r'^site/edit/(\d+)/$', 'SiteEdit'),
    (r'^admin/site/put/(\d+)/$', 'SitePut'),
    (r'^site/announcement/(\d+)/$', 'SiteAnnouncement'),
    (r'^site/scope_of_work/(\d+)/$', 'SiteScopeOfWork'),

    (r'^captain$', 'CaptainList'),
    (r'^captain/list$', 'CaptainList'),
    (r'^captain/autocomplete/$', 'CaptainAutocomplete'),
    (r'^captain/export$', 'CaptainExport'),
    (r'^captain/new$', 'CaptainNew'),
    (r'^captain/edit/(\d+)/$', 'CaptainEdit'),
    (r'^admin/captain/delete_confirm/(\d+)/$', 'CaptainDeleteConfirm'),
    (r'^admin/captain/delete/(\d+)/$', 'CaptainDelete'),
    (r'^admin/captain/put/(\d+)/$', 'CaptainPut'),
    (r'^captain/home/(\d+)/$', 'CaptainHome'),
    (r'^captain_home$', 'CaptainHome'),

    (r'^staff$', 'StaffList'),
    (r'^staff/list$', 'StaffList'),
    (r'^staff/new$', 'StaffNew'),
    (r'^staff/edit/(\d+)/$', 'StaffEdit'),

    (r'^supplier$', 'SupplierList'),
    (r'^supplier/list$', 'SupplierList'),
    (r'^supplier/new$', 'SupplierNew'),
    (r'^supplier/new-simple$', 'SupplierNewSimple'),
    (r'^supplier/edit/(\d+)/$', 'SupplierEdit'),

    (r'^inventory$', 'Inventory'),

    (r'^checkrequest/list/$', 'CheckRequestList'),
    (r'^checkrequest/list/(\d+)/$', 'CheckRequestList'),
    (r'^checkrequest/new/(\d+)/$', 'CheckRequestNew'),
    (r'^checkrequest/edit/(\d+)/$', 'CheckRequestEdit'),
    (r'^checkrequest/view/(\d+)/$', 'CheckRequestView'),

    (r'^vendorreceipt/list/$', 'VendorReceiptList'),
    (r'^vendorreceipt/list/(\d+)/$', 'VendorReceiptList'),
    (r'^vendorreceipt/new/(\d+)/$', 'VendorReceiptNew'),
    (r'^vendorreceipt/edit/(\d+)/$', 'VendorReceiptEdit'),
    (r'^vendorreceipt/view/(\d+)/$', 'VendorReceiptView'),

    (r'^inkinddonation/list/$', 'InKindDonationList'),
    (r'^inkinddonation/list/(\d+)/$', 'InKindDonationList'),
    (r'^inkinddonation/new/(\d+)/$', 'InKindDonationNew'),
    (r'^inkinddonation/edit/(\d+)/$', 'InKindDonationEdit'),
    (r'^inkinddonation/view/(\d+)/$', 'InKindDonationView'),

    (r'^siteexpense/state/(\w+)/(\d+)/$', 'SiteExpenseState'),
    (r'^expense/new/(\d+)/$', 'ExpenseNew'),
    (r'^expense/(\d+)/$', 'Expense'),
    )

urlpatterns += patterns(
    'room.order',
    (r'^order$', 'OrderList'),
    (r'^order/preview/(\d+)/$', 'OrderPreview'),
    (r'^order/list/.?$', 'OrderList'),
    (r'^order/list/(\d+)$', 'OrderList'),
    (r'^order/reconcile/(\d+)$', 'OrderReconcile'),
    (r'^order/actual_total/(\d+)$', 'ActualTotal'),
    (r'^order/reconciliation_notes/(\d+)$', 'ReconciliationNotes'),
    (r'^order/vendor/(\d+)$', 'Vendor'),
    (r'^order/invoice_date/(\d+)$', 'InvoiceDate'),
    (r'^order/state/(\d+)$', 'State'),
    (r'^order/export$', 'OrderExport'),
    (r'^order/new/(\d+)/$', 'OrderNew'),
    (r'^order/new/(\d+)/(\w+)/$', 'OrderNew'),
    (r'^order/edit/(\d+)/$', 'OrderEdit'),
    (r'^order/logistics/(\d+)/$', 'OrderLogistics'),
    (r'^order/view/(\d+)/$', 'OrderView'),
    (r'^order/delete/(\d+)/$', 'OrderDelete'),
    (r'^order/delete/(\d+)/(\d+)/$', 'OrderDelete'),
    (r'^order/deleteconfirm/$', 'OrderDeleteConfirm'),
    (r'^order/deleteconfirm/(\d+)/$', 'OrderDeleteConfirm'),
    (r'^order/fulfill/(\d+)/$', 'OrderFulfill'),
    (r'^order/fulfill/(\d+)/(\d+)/$', 'OrderFulfill'),
    (r'^order/fulfillconfirm/$', 'OrderFulfillConfirm'),
    (r'^order/fulfillconfirm/(\d+)/$', 'OrderFulfillConfirm'),
    (r'^order_item/name/$', 'OrderItemName'),
    (r'^admin/order/update_logistics/(\d+)/$', 'OrderUpdateLogistics'),
    )
