"""Main application, welcome screen."""
import logging
import os

import jinja2
import webapp2

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
        user, status = common.GetUser()
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

app = webapp2.WSGIApplication([
    webapp2.Route(r'/',
                  MainPage,
                  name='Start'),
    webapp2.Route(r'/help',
                  Placeholder,
                  name='Help'),  # TODO
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
                  MainPage,
                  name='Scoreboard'),  # TODO
    webapp2.Route(r'/scoreboard/all',
                  MainPage,
                  name='AllProgramsScoreboard'),  # TODO
    webapp2.Route(r'/help',
                  MainPage,
                  name='SiteNew'),  # TODO
    webapp2.Route(r'/site_list',
                  MainPage,
                  name='SiteList'),  # TODO
    webapp2.Route(r'/site_edit/<site_id:\d+>',
                  staff.Site,
                  name='SiteEdit'),  # TODO
    webapp2.Route(r'/site_expenses/<site_id:\d+>',
                  staff.Site,
                  name='SiteExpenses'),  # TODO
    webapp2.Route(r'/site_summary/<site_id:\d+>',
                  staff.Site,
                  name='SiteSummary'),  # TODO
    webapp2.Route(r'/site_view/<site_id:\d+>',
                  staff.Site,
                  name='SiteView'),  # TODO
    webapp2.Route(r'/help',
                  MainPage,
                  name='SiteBudget'),  # TODO
    webapp2.Route(r'/help',
                  MainPage,
                  name='SiteAnnouncement'),  # TODO
    webapp2.Route(r'/help',
                  MainPage,
                  name='SitesWithoutOrder'),  # TODO
    webapp2.Route(r'/help',
                  MainPage,
                  name='OrderEdit'),  # TODO
    webapp2.Route(r'/help',
                  MainPage,
                  name='OrderFulfill'),  # TODO
    webapp2.Route(r'/help',
                  MainPage,
                  name='OrderList'),  # TODO
    webapp2.Route(r'/help',
                  MainPage,
                  name='OrderNew'),  # TODO
    webapp2.Route(r'/help/<site:\d+>',
                  MainPage,
                  name='OrderPreview'),  # TODO
    webapp2.Route(r'/help',
                  MainPage,
                  name='CaptainList'),  # TODO
    webapp2.Route(r'/help',
                  MainPage,
                  name='CaptainNew'),  # TODO
    webapp2.Route(r'/help',
                  MainPage,
                  name='CaptainEdit'),  # TODO
    webapp2.Route(r'/help',
                  MainPage,
                  name='ItemList'),  # TODO
    webapp2.Route(r'/help',
                  MainPage,
                  name='ItemNew'),  # TODO
    webapp2.Route(r'/help',
                  MainPage,
                  name='OrderSheetList'),  # TODO
    webapp2.Route(r'/help',
                  MainPage,
                  name='OrderSheetNew'),  # TODO
    webapp2.Route(r'/help',
                  MainPage,
                  name='StaffList'),  # TODO
    webapp2.Route(r'/help',
                  MainPage,
                  name='StaffNew'),  # TODO
    webapp2.Route(r'/supplier',
                  staff.SupplierList,
                  name='SupplierList'),  # TODO
    webapp2.Route(r'/supplier/<supplier_id:\d*>',
                  staff.Supplier,
                  name='Supplier'),  # TODO
    webapp2.Route(r'/help',
                  MainPage,
                  name='CheckRequestList'),  # TODO
    webapp2.Route(r'/help',
                  MainPage,
                  name='CheckRequestView'),  # TODO
    webapp2.Route(r'/help',
                  MainPage,
                  name='CheckRequestEdit'),  # TODO
    webapp2.Route(r'/help',
                  MainPage,
                  name='CheckRequestNew'),  # TODO
    webapp2.Route(r'/help',
                  MainPage,
                  name='InKindDonationList'),  # TODO
    webapp2.Route(r'/help',
                  MainPage,
                  name='InKindDonationView'),  # TODO
    webapp2.Route(r'/help',
                  MainPage,
                  name='InKindDonationNew'),  # TODO
    webapp2.Route(r'/help',
                  MainPage,
                  name='VendorReceiptList'),  # TODO
    webapp2.Route(r'/help',
                  MainPage,
                  name='VendorReceiptView'),  # TODO
    webapp2.Route(r'/help',
                  MainPage,
                  name='VendorReceiptNew'),  # TODO
    webapp2.Route(r'/help',
                  MainPage,
                  name='StaffTimeList'),  # TODO
    webapp2.Route(r'/help',
                  MainPage,
                  name='StaffTimeView'),  # TODO
    webapp2.Route(r'/help',
                  MainPage,
                  name='StaffTimeNew'),  # TODO
] + [webapp2.Route(r'/help',
                   MainPage,
                   name='%sEdit' % kind) for kind in EXPENSE_KINDS
    ], debug=True)

