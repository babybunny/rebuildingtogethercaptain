"""Main application, welcome screen."""
import os

import jinja2
import webapp2
from google.appengine.api import users
from webapp2_extras import routes

from room import captain
from room import common
from room import staff

EXPENSE_KINDS = (
  # 'CheckRequest',
  'VendorReceipt', 'InKindDonation', 'StaffTime')


class MainPage(webapp2.RequestHandler):
  """The main UI page, renders the 'index.html' template."""

  def get(self):
    """Renders the main page."""
    user = common.RoomsUser.from_request(self.request)
    if user and user.staff:
      self.redirect_to('StaffHome')
    if user and user.captain:
      self.redirect_to('CaptainHome')
    login_url = users.create_login_url('/')
    logout_url = users.create_logout_url('/')
    template_values = dict(locals())
    template = jinja_environment.get_template('templates/welcome.html')
    self.response.out.write(template.render(template_values))


class Placeholder(webapp2.RequestHandler):
  def get(self):
    self.response.out.write('Placeholder')


jinja_environment = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

# Be sure to also configure the /room path with login: required in app.yaml.
login_required = routes.PathPrefixRoute('/room', [
  webapp2.Route(r'/staff_home',
                staff.StaffHome,
                name='StaffHome'),
  webapp2.Route(r'/select_program',
                staff.SelectProgram,
                name='SelectProgram'),
  webapp2.Route(r'/captain_autocomplete',
                staff.CaptainAutocomplete,
                name='CaptainAutocomplete'),
  webapp2.Route(r'/site_autocomplete',
                staff.SiteAutocomplete,
                name='SiteAutocomplete'),
  webapp2.Route(r'/captain_home',
                captain.CaptainHome,
                name='CaptainHome'),

  webapp2.Route(r'/staff',
                staff.StaffList,
                name='StaffList'),
  webapp2.Route(r'/staff/<id:\d*>',
                staff.Staff,
                name='Staff'),

  webapp2.Route(r'/captain',
                staff.CaptainList,
                name='CaptainList'),
  webapp2.Route(r'/captain/<id:\d*>',
                staff.Captain,
                name='Captain'),

  webapp2.Route(r'/supplier',
                staff.SupplierList,
                name='SupplierList'),
  webapp2.Route(r'/supplier/<id:\d*>',
                staff.Supplier,
                name='Supplier'),

  webapp2.Route(r'/program',
                staff.ProgramList,
                name='ProgramList'),
  webapp2.Route(r'/program/<id:\d*>',
                staff.Program,
                name='Program'),

  webapp2.Route(r'/ordersheet',
                staff.OrderSheetList,
                name='OrderSheetList'),
  webapp2.Route(r'/ordersheet/<id:\d*>',
                staff.OrderSheet,
                name='OrderSheet'),

  webapp2.Route(r'/order_picklist',
                staff.OrderPicklist,
                name='OrderBySheet'),
  webapp2.Route(r'/order_view/<id:\d+>',
                staff.OrderView,
                name='OrderView'),
  webapp2.Route(r'/order_delete/<order_id:\d+>',
                staff.OrderDelete,
                name='OrderDelete'),
  webapp2.Route(r'/order_fulfill/<order_id:\d+>',
                staff.OrderFulfill,
                name='OrderFulfill'),
  webapp2.Route(r'/order_reconcile/<order_sheet_id:\d+>',
                staff.OrderReconcile,
                name='OrderReconcile'),
  webapp2.Route(r'/order_invoice/<order_id:\d+>',
                staff.OrderInvoice,
                name='OrderInvoice'),

  webapp2.Route(r'/order/actualtotal/<order_id:\d+>',
                staff.ActualTotal,
                name='ActualTotal'),
  webapp2.Route(r'/order/reconciliationnotes/<order_id:\d+>',
                staff.ReconciliationNotes,
                name='ReconciliationNotes'),
  webapp2.Route(r'/order/invoicedate/<order_id:\d+>',
                staff.InvoiceDate,
                name='InvoiceDate'),
  webapp2.Route(r'/order/state/<order_id:\d+>',
                staff.State,
                name='State'),
  webapp2.Route(r'/order/vendor/<order_id:\d+>',
                staff.Vendor,
                name='Vendor'),

  webapp2.Route(r'/site/<site_id:\d+>/order',
                staff.OrderList,
                name='OrderBySite'),
  webapp2.Route(r'/site/<site_id:\d+>/order/<id:\d*>',
                staff.Order,
                name='Order'),
  webapp2.Route(r'/site/<site_id:\d+>/order_flow/<id:\d*>',
                staff.OrderFlow,
                name='OrderFlow'),

  webapp2.Route(r'/stafftime_by_program',
                staff.StaffTimeList,
                name='StaffTimeByProgram'),
  webapp2.Route(r'/stafftime_view/<id:\d+>',
                staff.StaffTimeView,
                name='StaffTimeView'),
  webapp2.Route(r'/site/<site_id:\d+>/stafftime',
                staff.StaffTimeList,
                name='StaffTimeBySite'),
  webapp2.Route(r'/site/<site_id:\d+>/stafftime/<id:\d*>',
                staff.StaffTime,
                name='StaffTime'),

  webapp2.Route(r'/checkrequest_by_program',
                staff.CheckRequestList,
                name='CheckRequestByProgram'),
  webapp2.Route(r'/checkrequest_view/<id:\d+>',
                staff.CheckRequestView,
                name='CheckRequestView'),
  webapp2.Route(r'/site/<site_id:\d+>/checkrequest',
                staff.CheckRequestList,
                name='CheckRequestBySite'),
  webapp2.Route(r'/site/<site_id:\d+>/checkrequest/<id:\d*>',
                staff.CheckRequest,
                name='CheckRequest'),

  webapp2.Route(r'/vendorreceipt_by_program',
                staff.VendorReceiptList,
                name='VendorReceiptByProgram'),
  webapp2.Route(r'/vendorreceipt_view/<id:\d+>',
                staff.VendorReceiptView,
                name='VendorReceiptView'),
  webapp2.Route(r'/site/<site_id:\d+>/vendorreceipt',
                staff.VendorReceiptList,
                name='VendorReceiptBySite'),
  webapp2.Route(r'/site/<site_id:\d+>/vendorreceipt/<id:\d*>',
                staff.VendorReceipt,
                name='VendorReceipt'),

  webapp2.Route(r'/inkinddonation_by_program',
                staff.InKindDonationList,
                name='InKindDonationByProgram'),
  webapp2.Route(r'/inkinddonation_view/<id:\d+>',
                staff.InKindDonationView,
                name='InKindDonationView'),
  webapp2.Route(r'/site/<site_id:\d+>/inkinddonation',
                staff.InKindDonationList,
                name='InKindDonationBySite'),
  webapp2.Route(r'/site/<site_id:\d+>/inkinddonation/<id:\d*>',
                staff.InKindDonation,
                name='InKindDonation'),

  webapp2.Route(r'/item',
                staff.ItemList,
                name='ItemList'),
  webapp2.Route(r'/item/<id:\d*>',
                staff.Item,
                name='Item'),

  webapp2.Route(r'/staffposition',
                staff.StaffPositionList,
                name='StaffPositionList'),
  webapp2.Route(r'/staffposition/<id:\d*>',
                staff.StaffPosition,
                name='StaffPosition'),

  # webapp2.Route(r'/example',
  #               staff.ExampleList,
  #               name='ExampleList'),
  # webapp2.Route(r'/example/<id:\d*>',
  #               staff.Example,
  #               name='Example'),


  webapp2.Route(r'/site/view/<id:\d+>/',
                staff.SiteView,
                name='SiteView'),
  webapp2.Route(r'/site/attachments/<id:\d+>',
                staff.SiteAttachments,
                name=staff.SiteAttachments.__name__),
  webapp2.Route(r'/site/lookup/<site_number:\w+>',
                staff.SiteLookup,
                name='SiteLookup'),
  webapp2.Route(r'/site/list/<id:\d+>/',  # back compat
                staff.SiteView,
                name='SiteViewBackCompat'),
  webapp2.Route(r'/site/<id:\d*>',
                staff.Site,
                name='Site'),

  webapp2.Route(r'/site_expenses/<id:\d+>',
                staff.SiteExpenses,
                name='SiteExpenses'),

  webapp2.Route(r'/site_summary/<id:\d+>',
                staff.SiteSummary,
                name='SiteSummary'),

  webapp2.Route(r'/site_scope_of_work/<id:\d+>',
                staff.SiteScopeOfWork,
                name='SiteScopeOfWork'),

  webapp2.Route(r'/site_expense_state/<:\w+>/<:\d+>',
                staff.SiteExpenseState,
                name='SiteExpenseState'),  # TODO

  webapp2.Route(r'/sites_and_captains',
                staff.SitesAndCaptains,
                name='SitesAndCaptains'),
  webapp2.Route(r'/ordersheet_items/<id:\d+>',
                staff.OrderSheetItemList,
                name='OrderSheetItemList'),

  webapp2.Route(r'/site_budget',
                staff.SiteBudget,
                name='SiteBudget'),

  webapp2.Route(r'/scoreboard',
                Placeholder,
                name='Scoreboard'),  # TODO
  webapp2.Route(r'/scoreboard/all',
                Placeholder,
                name='AllProgramsScoreboard'),  # TODO
  webapp2.Route(r'/help',
                Placeholder,
                name='SiteNew'),  # TODO
  webapp2.Route(r'/item_thumbnail',
                Placeholder,
                name='ItemThumbnail'),  # TODO
  webapp2.Route(r'/site_list',
                Placeholder,
                name='SiteList'),  # TODO
  webapp2.Route(r'/help',
                Placeholder,
                name='SiteExport'),  # TODO
  webapp2.Route(r'/help',
                Placeholder,
                name='SiteAnnouncement'),  # TODO
  webapp2.Route(r'/help',
                Placeholder,
                name='SitesWithoutOrder'),  # TODO
  webapp2.Route(r'/help',
                Placeholder,
                name='OrderEdit'),  # TODO
  webapp2.Route(r'/help',
                Placeholder,
                name='OrderNew'),  # TODO
  webapp2.Route(r'/help/<site:\d+>',
                Placeholder,
                name='OrderPreview'),  # TODO
  webapp2.Route(r'/help',
                Placeholder,
                name='CaptainExport'),  # TODO
  webapp2.Route(r'/help',
                Placeholder,
                name='OrderExport'),  # TODO
  webapp2.Route(r'/help',
                Placeholder,
                name='StaffNew'),  # TODO
  webapp2.Route(r'/search',
                staff.Search,
                name='Search'),
  webapp2.Route(r'/load_model/<model_type:\w+>/<model_id:\d+>',
                staff.LoadModel,
                name='LoadModel')
])

post_routes = routes.PathPrefixRoute('/room', [
  webapp2.Route(r'/room/site_budget_export',
                staff.SiteBudgetExport,
                name='SiteBudgetExport')
])

non_standard_routes = routes.PathPrefixRoute('/room', [
  webapp2.Route(r'/site/attachments/upload',
                staff.UploadSiteAttachment,
                name=staff.UploadSiteAttachment.__name__),
  webapp2.Route(r'/site/attachments/download',
                staff.DownloadSiteAttachment,
                name=staff.DownloadSiteAttachment.__name__),
  webapp2.Route(r'/site/attachments/remove',
                staff.RemoveSiteAttachment,
                name=staff.RemoveSiteAttachment.__name__)
])

app = webapp2.WSGIApplication(
  [
    webapp2.Route(r'/',
                  MainPage,
                  name='Start'),
    webapp2.Route(r'/help',
                  Placeholder,
                  name='Help'),  # TODO
    login_required,
    post_routes,
    non_standard_routes,
    webapp2.Route(r'/order_delete_confirm',
                  staff.OrderDeleteConfirm,
                  name='OrderDeleteConfirm'),
    webapp2.Route(r'/order_fulfill_confirm',
                  staff.OrderFulfillConfirm,
                  name='OrderFulfillConfirm'),
  ],
  debug=True)
