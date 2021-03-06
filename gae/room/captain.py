import logging
import webapp2

import common
import ndb_models


def _AnnotateSitesWithEditability(entries, captain, staff):
  for site in entries:
    if staff or (captain and site.sitecaptain_set
                 and captain in [sc.captain for sc in site.sitecaptain_set]):
      site.editable_by_current_user = True
    else:
      site.editable_by_current_user = False


class CaptainHandler(webapp2.RequestHandler):
  """Handler base class that ensures the user meets Captain view prerequisites:
  - user is logged in
  - user matches an existing Captain or Staff record
  """

  def dispatch(self, *a, **k):
    user = common.RoomsUser.from_request(self.request)
    if user and (user.staff or user.captain):
      super(CaptainHandler, self).dispatch(*a, **k)
    else:
      return webapp2.redirect_to('Start')


class CaptainHome(CaptainHandler):
  def get(self, captain_id=None):
    user = common.RoomsUser.from_request(self.request)
    if user is None or user.captain is None:
      return webapp2.redirect_to('Start')
    captain = user.captain
    if captain_id is not None:
      captain = ndb_models.Captain.get_by_id(int(captain_id))
    order_sheets = ndb_models.OrderSheet.query().order(ndb_models.OrderSheet.name)
    sites = {}
    scs = list(ndb_models.SiteCaptain.query(
      ndb_models.SiteCaptain.captain == captain.key))
    for sitecaptain in scs:
      site = sitecaptain.site.get()
      
      if site.program_key:
        program = site.program_key.get()
      else:
        program = ndb_models.Program.query(ndb_models.Program.name == site.program).get()
      if not program:
        logging.warning('unable to find program for site %s', site.number)
        continue
      if program.status != ndb_models.Program.ACTIVE_STATUS:
        logging.info('skipping inactive site %s in program %s %s', site.number, program.name, program.status)
        continue
          

      # TODO:what's this? maybe clean it up.
      site.new_order_form = "site.new_order_form placeholder"

      sites[site.number] = site

    if not sites:
      logging.warning('no sites in active programs. but found SiteCaptains: %s', scs)
      
    captain_form = 'captain_form placeholder'
    return common.Respond(self.request, 'captain_home',
                          {'order_sheets': order_sheets,
                           'entries': sorted(sites.values(), key=lambda(s): s.number),
                           'captain': captain,
                           'captain_form': captain_form,
                           'captain_contact_submit':
                             'Save changes to personal info',
                           'map_width': common.MAP_WIDTH, 'map_height': common.MAP_HEIGHT,
                           'site_list_detail': True,
                           'start_new_order_submit': common.START_NEW_ORDER_SUBMIT,
                           })
