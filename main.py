"""Main application, welcome screen."""
import logging
import os

import jinja2
import webapp2
from webapp2_extras import routes

from room import common
from room import ndb_models
from room import staff
from room import captain
# from room import views

from google.appengine.api import users


EXPENSE_KINDS = ('CheckRequest', 'VendorReceipt', 'InKindDonation', 'StaffTime')


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
    webapp2.Route(r'/scoreboard',
                  Placeholder,
                  name='Scoreboard'),  # TODO
    webapp2.Route(r'/scoreboard/all',
                  Placeholder,
                  name='AllProgramsScoreboard'),  # TODO

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
    
    
    # webapp2.Route(r'/example',
    #               staff.ExampleList,
    #               name='ExampleList'),
    # webapp2.Route(r'/example/<id:\d*>',
    #               staff.Example,
    #               name='Example'),

    
    webapp2.Route(r'/site/<id:\d+>/',
                  staff.SiteView,
                  name='SiteView'),
    webapp2.Route(r'/site/list/<id:\d+>/',  # back compat
                  staff.SiteView,
                  name='SiteViewBackCompat'),
    
    webapp2.Route(r'/sites_and_captains',
                  staff.SitesAndCaptains,
                  name='SitesAndCaptains'),
    
    webapp2.Route(r'/help',
                  Placeholder,
                  name='SiteNew'),  # TODO
    webapp2.Route(r'/site_list',
                  Placeholder,
                  name='SiteList'),  # TODO
    webapp2.Route(r'/help',
                  Placeholder,
                  name='SiteExport'),  # TODO
    webapp2.Route(r'/site/edit/<id:\d+>/',
                  staff.Site,
                  name='SiteEdit'),  # TODO
    webapp2.Route(r'/site_expenses/<id:\d+>',
                  staff.Site,
                  name='SiteExpenses'),  # TODO
    webapp2.Route(r'/site_summary/<id:\d+>',
                  staff.Site,
                  name='SiteSummary'),  # TODO
    webapp2.Route(r'/help',
                  Placeholder,
                  name='SiteBudget'),  # TODO
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
                  name='OrderFulfill'),  # TODO
    webapp2.Route(r'/help',
                  Placeholder,
                  name='OrderList'),  # TODO
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
                  name='CaptainNew'),  # TODO
    webapp2.Route(r'/help',
                  Placeholder,
                  name='CaptainEdit'),  # TODO
    webapp2.Route(r'/help',
                  Placeholder,
                  name='ItemList'),  # TODO
    webapp2.Route(r'/help',
                  Placeholder,
                  name='ItemNew'),  # TODO
    webapp2.Route(r'/help',
                  Placeholder,
                  name='OrderSheetList'),  # TODO
    webapp2.Route(r'/help',
                  Placeholder,
                  name='OrderSheetNew'),  # TODO
    webapp2.Route(r'/help',
                  Placeholder,
                  name='StaffNew'),  # TODO
    webapp2.Route(r'/help',
                  Placeholder,
                  name='CheckRequestList'),  # TODO
    webapp2.Route(r'/help',
                  Placeholder,
                  name='CheckRequestView'),  # TODO
    webapp2.Route(r'/help',
                  Placeholder,
                  name='CheckRequestEdit'),  # TODO
    webapp2.Route(r'/help',
                  Placeholder,
                  name='CheckRequestNew'),  # TODO
    webapp2.Route(r'/help',
                  Placeholder,
                  name='InKindDonationList'),  # TODO
    webapp2.Route(r'/help',
                  Placeholder,
                  name='InKindDonationView'),  # TODO
    webapp2.Route(r'/help',
                  Placeholder,
                  name='InKindDonationNew'),  # TODO
    webapp2.Route(r'/help',
                  Placeholder,
                  name='VendorReceiptList'),  # TODO
    webapp2.Route(r'/help',
                  Placeholder,
                  name='VendorReceiptView'),  # TODO
    webapp2.Route(r'/help',
                  Placeholder,
                  name='VendorReceiptNew'),  # TODO
    webapp2.Route(r'/help',
                  Placeholder,
                  name='StaffTimeList'),  # TODO
    webapp2.Route(r'/help',
                  Placeholder,
                  name='StaffTimeView'),  # TODO
    webapp2.Route(r'/help',
                  Placeholder,
                  name='StaffTimeNew'),  # TODO
] + [webapp2.Route(r'/help',
                   Placeholder,
                   name='%sEdit' % kind) for kind in EXPENSE_KINDS
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
    ], 
    debug=True)

