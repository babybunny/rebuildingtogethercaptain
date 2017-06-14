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


def CaptainHome(request, captain_id=None):
  user, _ = common.GetUser(self.request)
  if user is None or user.captain is None:
    return webapp2.redirect_to('Start')
  captain = user.captain
  if captain_id is not None:
    captain = ndb_models.Captain.get_by_id(int(captain_id))
  order_sheets = ndb_models.OrderSheet.query().order(ndb_models.OrderSheet.name)
  sites = []
  for sitecaptain in ndb_models.SiteCaptain.query(
      ndb_models.SiteCaptain.captain == captain.key):
    site = sitecaptain.site.get()
    # if site.program != common.DEFAULT_CAPTAIN_PROGRAM:
    #   continue
    # site.new_order_form = forms.NewOrderForm(initial=dict(site=site.key()))
    site.new_order_form = "site.new_order_form placeholder"
    sites.append(site)

  #   _AnnotateSitesWithEditability(sites, captain, staff)
  for site in sites:
    site.editable_by_current_user = True
    site.sitecaptain_set = ndb_models.SiteCaptain.query(
      ndb_models.SiteCaptain.site == site.key)
    
  # captain_form = forms.CaptainContactForm(data=request.POST or None,
  #                                         instance=captain)
  captain_form = 'captain_form placeholder'
  return common.Respond(request, 'captain_home',
                        {'order_sheets': order_sheets,
                         'entries': sites,
                         'captain': captain,
                         'captain_form': captain_form,
                         'captain_contact_submit':
                         'Save changes to personal info',
                         'map_width': common.MAP_WIDTH, 'map_height': common.MAP_HEIGHT,
                         'site_list_detail': True,
                         'start_new_order_submit': common.START_NEW_ORDER_SUBMIT,
                         })

