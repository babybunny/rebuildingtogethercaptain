"""Main application, welcome screen."""
import os

import jinja2
import webapp2
from google.appengine.api import users
from webapp2_extras import routes

from room import captain, ndb_models
from room import common
from room import staff

# from room import views

EXPENSE_KINDS = (
  # 'CheckRequest',
  'VendorReceipt', 'InKindDonation', 'StaffTime')


class MainPage(webapp2.RequestHandler):
  """The main UI page, renders the 'index.html' template."""

  def get(self):
    """Renders the main page."""
    user, status = common.GetUser(self.request)
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


class TestableRoute(webapp2.Route):

  def __init__(self,
               # builtin webapp2.Route parameters
               template,
               handler=None,
               name=None,
               defaults=None,
               build_only=False,
               handler_method=None,
               methods=None,
               schemes=None,

               # add-ons for testing
               url_params=None,
               post_data=None):

    self.url_params = url_params
    self.post_data = post_data
    super(TestableRoute, self).__init__(template, handler=handler, name=name, defaults=defaults, build_only=build_only,
                                        handler_method=handler_method, methods=methods, schemes=schemes)

jinja_environment = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

# Be sure to also configure the /room path with login: required in app.yaml.
login_required = routes.PathPrefixRoute('/room', [
  webapp2.Route(r'/staff_home',
                staff.StaffHome,
                name='StaffHome',
                methods=['GET']),
  webapp2.Route(r'/select_program',
                staff.SelectProgram,
                name='SelectProgram',
                methods=['GET']),
  webapp2.Route(r'/captain_autocomplete',
                staff.CaptainAutocomplete,
                name='CaptainAutocomplete',
                methods=['GET']),
  webapp2.Route(r'/site_autocomplete',
                staff.SiteAutocomplete,
                name='SiteAutocomplete',
                methods=['GET']),
  webapp2.Route(r'/captain_home',
                captain.CaptainHome,
                name='CaptainHome',
                methods=['GET']),

  webapp2.Route(r'/staff',
                staff.StaffList,
                name='StaffList',
                methods=['GET']),
  TestableRoute(r'/staff?id=<id:\d*>',
                staff.Staff,
                name='Staff',
                url_params={'test_models_key': 'STAFF',
                            'parameter': 'id',
                            'base_path': r'/staff'}),

  webapp2.Route(r'/captain',
                staff.CaptainList,
                name='CaptainList',
                methods=['GET']),
  webapp2.Route(r'/captain/<id:\d*>',
                staff.Captain,
                name='Captain',
                methods=['GET']),

  webapp2.Route(r'/supplier',
                staff.SupplierList,
                name='SupplierList',
                methods=['GET']),
  webapp2.Route(r'/supplier/<id:\d*>',
                staff.Supplier,
                name='Supplier',
                methods=['GET']),

  webapp2.Route(r'/ordersheet',
                staff.OrderSheetList,
                name='OrderSheetList',
                methods=['GET']),
  webapp2.Route(r'/ordersheet/<id:\d*>',
                staff.OrderSheet,
                name='OrderSheet',
                methods=['GET']),

  webapp2.Route(r'/order_picklist',
                staff.OrderPicklist,
                name='OrderBySheet',
                methods=['GET']),
  webapp2.Route(r'/order_picklist',
                staff.OrderPicklist,
                name='OrderByProgram',
                methods=['GET']),
  webapp2.Route(r'/order_view/<id:\d+>',
                staff.OrderView,
                name='OrderView',
                methods=['GET']),
  webapp2.Route(r'/order_delete/<order_id:\d+>',
                staff.OrderDelete,
                name='OrderDelete',
                methods=['GET']),
  webapp2.Route(r'/order_fulfill/<order_id:\d+>',
                staff.OrderFulfill,
                name='OrderFulfill',
                methods=['GET']),
  webapp2.Route(r'/order_reconcile/<order_sheet_id:\d+>',
                staff.OrderReconcile,
                name='OrderReconcile',
                methods=['GET']),

  webapp2.Route(r'/order/actualtotal/<order_id:\d+>',
                staff.ActualTotal,
                name='ActualTotal',
                methods=['GET']),
  webapp2.Route(r'/order/reconciliationnotes/<order_id:\d+>',
                staff.ReconciliationNotes,
                name='ReconciliationNotes',
                methods=['GET']),
  webapp2.Route(r'/order/invoicedate/<order_id:\d+>',
                staff.InvoiceDate,
                name='InvoiceDate',
                methods=['GET']),
  webapp2.Route(r'/order/state/<order_id:\d+>',
                staff.State,
                name='State',
                methods=['GET']),
  webapp2.Route(r'/order/vendor/<order_id:\d+>',
                staff.Vendor,
                name='Vendor',
                methods=['GET']),

  webapp2.Route(r'/site/<site_id:\d+>/order',
                staff.OrderList,
                name='OrderBySite',
                methods=['GET']),
  webapp2.Route(r'/site/<site_id:\d+>/order/<id:\d*>',
                staff.Order,
                name='Order',
                methods=['GET']),
  webapp2.Route(r'/site/<site_id:\d+>/order_flow/<id:\d*>',
                staff.OrderFlow,
                name='OrderFlow',
                methods=['GET']),

  webapp2.Route(r'/stafftime_by_program',
                staff.StaffTimeList,
                name='StaffTimeByProgram',
                methods=['GET']),
  webapp2.Route(r'/stafftime_view/<id:\d+>',
                staff.StaffTimeView,
                name='StaffTimeView',
                methods=['GET']),
  webapp2.Route(r'/site/<site_id:\d+>/stafftime',
                staff.StaffTimeList,
                name='StaffTimeBySite',
                methods=['GET']),
  webapp2.Route(r'/site/<site_id:\d+>/stafftime/<id:\d*>',
                staff.StaffTime,
                name='StaffTime',
                methods=['GET']),

  webapp2.Route(r'/checkrequest_by_program',
                staff.CheckRequestList,
                name='CheckRequestByProgram',
                methods=['GET']),
  webapp2.Route(r'/checkrequest_view/<id:\d+>',
                staff.CheckRequestView,
                name='CheckRequestView',
                methods=['GET']),
  webapp2.Route(r'/site/<site_id:\d+>/checkrequest',
                staff.CheckRequestList,
                name='CheckRequestBySite',
                methods=['GET']),
  webapp2.Route(r'/site/<site_id:\d+>/checkrequest/<id:\d*>',
                staff.CheckRequest,
                name='CheckRequest',
                methods=['GET']),

  webapp2.Route(r'/vendorreceipt_by_program',
                staff.VendorReceiptList,
                name='VendorReceiptByProgram',
                methods=['GET']),
  webapp2.Route(r'/vendorreceipt_view/<id:\d+>',
                staff.VendorReceiptView,
                name='VendorReceiptView',
                methods=['GET']),
  webapp2.Route(r'/site/<site_id:\d+>/vendorreceipt',
                staff.VendorReceiptList,
                name='VendorReceiptBySite',
                methods=['GET']),
  webapp2.Route(r'/site/<site_id:\d+>/vendorreceipt/<id:\d*>',
                staff.VendorReceipt,
                name='VendorReceipt',
                methods=['GET']),

  webapp2.Route(r'/inkinddonation_by_program',
                staff.InKindDonationList,
                name='InKindDonationByProgram',
                methods=['GET']),
  webapp2.Route(r'/inkinddonation_view/<id:\d+>',
                staff.InKindDonationView,
                name='InKindDonationView',
                methods=['GET']),
  webapp2.Route(r'/site/<site_id:\d+>/inkinddonation',
                staff.InKindDonationList,
                name='InKindDonationBySite',
                methods=['GET']),
  webapp2.Route(r'/site/<site_id:\d+>/inkinddonation/<id:\d*>',
                staff.InKindDonation,
                name='InKindDonation',
                methods=['GET']),

  webapp2.Route(r'/item',
                staff.ItemList,
                name='ItemList',
                methods=['GET']),
  webapp2.Route(r'/item/<id:\d*>',
                staff.Item,
                name='Item',
                methods=['GET']),

  # webapp2.Route(r'/example',
  #               staff.ExampleList,
  #               name='ExampleList'),
  # webapp2.Route(r'/example/<id:\d*>',
  #               staff.Example,
  #               name='Example'),


  webapp2.Route(r'/site/view',
                staff.SiteView,
                name='SiteView',
                methods=['GET']),
  webapp2.Route(r'/site/lookup/<site_number:\w+>',
                staff.SiteLookup,
                name='SiteLookup',
                methods=['GET']),
  webapp2.Route(r'/site/list/<id:\d+>/',  # back compat
                staff.SiteView,
                name='SiteViewBackCompat',
                methods=['GET']),
  webapp2.Route(r'/site/<id:\d*>',
                staff.Site,
                name='Site',
                methods=['GET']),

  webapp2.Route(r'/site_expenses/<id:\d+>',
                staff.SiteExpenses,
                name='SiteExpenses',
                methods=['GET']),

  webapp2.Route(r'/site_summary/<id:\d+>',
                staff.SiteSummary,
                name='SiteSummary',
                methods=['GET']),

  webapp2.Route(r'/site_scope_of_work/<id:\d+>',
                staff.SiteScopeOfWork,
                name='SiteScopeOfWork',
                methods=['GET']),

  webapp2.Route(r'/site_expense_state/<:\w+>/<:\d+>',
                staff.SiteExpenseState,
                name='SiteExpenseState'),  # TODO

  webapp2.Route(r'/sites_and_captains',
                staff.SitesAndCaptains,
                name='SitesAndCaptains',
                methods=['GET']),
  webapp2.Route(r'/ordersheet_items/<id:\d+>',
                staff.OrderSheetItemList,
                name='OrderSheetItemList',
                methods=['GET']),

  webapp2.Route(r'/site_budget',
                staff.SiteBudget,
                name='SiteBudget',
                methods=['GET']),

  webapp2.Route(r'/scoreboard',
                Placeholder,
                name='Scoreboard',
                methods=['GET']),  # TODO
  webapp2.Route(r'/scoreboard/all',
                Placeholder,
                name='AllProgramsScoreboard',
                methods=['GET']),  # TODO
  webapp2.Route(r'/help',
                Placeholder,
                name='SiteNew',
                methods=['GET']),  # TODO
  webapp2.Route(r'/item_thumbnail',
                Placeholder,
                name='ItemThumbnail',
                methods=['GET']),  # TODO
  webapp2.Route(r'/site_list',
                Placeholder,
                name='SiteList',
                methods=['GET']),  # TODO
  webapp2.Route(r'/help',
                Placeholder,
                name='SiteExport',
                methods=['GET']),  # TODO
  webapp2.Route(r'/help',
                Placeholder,
                name='SiteAnnouncement',
                methods=['GET']),  # TODO
  webapp2.Route(r'/help',
                Placeholder,
                name='SitesWithoutOrder',
                methods=['GET']),  # TODO
  webapp2.Route(r'/help',
                Placeholder,
                name='OrderEdit',
                methods=['GET']),  # TODO
  webapp2.Route(r'/help',
                Placeholder,
                name='OrderNew',
                methods=['GET']),  # TODO
  webapp2.Route(r'/help/<site:\d+>',
                Placeholder,
                name='OrderPreview',
                methods=['GET']),  # TODO
  webapp2.Route(r'/help',
                Placeholder,
                name='CaptainExport',
                methods=['GET']),  # TODO
  webapp2.Route(r'/help',
                Placeholder,
                name='OrderExport',
                methods=['GET']),  # TODO
  webapp2.Route(r'/help',
                Placeholder,
                name='CaptainNew',
                methods=['GET']),  # TODO
  webapp2.Route(r'/help',
                Placeholder,
                name='CaptainEdit',
                methods=['GET']),  # TODO
  webapp2.Route(r'/help',
                Placeholder,
                name='StaffNew',
                methods=['GET']),  # TODO
  TestableRoute(r'/room/site_budget_export',
                staff.SiteBudgetExport,
                name='SiteBudgetExport',
                post_data={'submit': staff.EXPORT_CSV},
                methods=['POST'])
])

app = webapp2.WSGIApplication(
  [
    webapp2.Route(r'/',
                  MainPage,
                  name='Start',
                  methods=['GET']),
    webapp2.Route(r'/help',
                  Placeholder,
                  name='Help',
                  methods=['GET']),  # TODO
    login_required,
    webapp2.Route(r'/order_delete_confirm',
                  staff.OrderDeleteConfirm,
                  name='OrderDeleteConfirm',
                  methods=['GET']),
    webapp2.Route(r'/order_fulfill_confirm',
                  staff.OrderFulfillConfirm,
                  name='OrderFulfillConfirm',
                  methods=['GET']),
  ],
  debug=True)
