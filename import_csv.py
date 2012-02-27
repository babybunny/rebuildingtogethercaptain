"""
Imports site and captain data into ROOM.  
Intended to be run with the remote_api:
bash> export PYTHONPATH=.:$PYTHONPATH
bash> python $(which remote_api_shell.py) -s rebuildingtogethercaptain.appspot.com
# or for development..
bash> python $(which remote_api_shell.py) -s localhost:8081 
dev~rebuildingtogethercaptain> reload(import_csv)
<module 'import_csv' from '/Users/babybunny/appengine/rebuildingtogethercaptain/import_csv.py'>
dev~rebuildingtogethercaptain> import_csv.import_sites(input_csv="../2012_ROOMS_site_info_sample.csv")
dev~rebuildingtogethercaptain> import_csv.import_captains(input_csv="../2012_ROOMS_Captain_email_sample.csv")
"""

import csv
import logging
import main  # to initialize Django
from room import models
from google.appengine.ext import db

PROGRAM = '2012 NRD'

def import_sites(input_csv="../2012_ROOMS_site_info_sample.csv"):
    """Change input_csv to actual input file - the default is test data."""
    reader = csv.DictReader(open(input_csv))
    for s in reader:
      number = s["Project::zProject_ID"]
      site = models.NewSite.all().filter('number =', number).get()
      if site:
          logging.info('site %s exists, skipping', number)
          continue
      else:
          site = models.NewSite(number=number)
      site.program = PROGRAM
      site.budget = int(s["Project::Project_Budget"])

      def clean_s(k):
          return s[k].replace('\n', ' ').replace('\xe2', "'").replace('\x80', "'").replace('\x99', '').encode('ascii', 'replace')

      site.name = clean_s("Applicant's_Party_Record::Name ComposedTwoLinesWAKA")
      site.street_number = clean_s("Address::Street Line")
      site.city_state_zip = "%s CA, %s" % (
          clean_s("Address::City"), clean_s("Address::zip"))
      site.applicant_home_phone = clean_s("Applicant's_Phone_Home::number")
      site.applicant_work_phone = clean_s("Applicant's_Phone_Work::number")
      site.applicant_mobile_phone = clean_s("Applicant's_Phone_Mobile::number")
      site.applicant_email = clean_s("Applicant's_email::email")
      site.sponsor = clean_s("project_Sponsorships_donorPartyRecord::Name Composed Simple")
      site.rating = clean_s("Rating")
      site.rrp_test = clean_s("RRP Is_Testing Required")
      site.rrp_level = clean_s("RRP Level")
      site.roof = clean_s("Roof_Request_Professional_Evaluation")
      site.jurisdiction = clean_s("Project::Project Jurisdiction")
      site.put()
      logging.info('put site %s', number)

def import_captains(input_csv="../2012_ROOMS_Captain_email_sample.csv"):
    """Change input_csv to actual input file - the default is test data."""
    reader = csv.DictReader(open(input_csv))
    for s in reader:
      def clean_s(k):
          return s[k].replace('\n', ' ').replace('\xe2', "'").replace('\x80', "'").replace('\x99', '').encode('ascii', 'replace')

      key = s['key']
      name = "%s %s" % (clean_s("PartyIFindividual::First Name"),
                        clean_s("PartyIFindividual::Last Name"))
      email = s["Email"]
      captain = None
      if key:
          captain = models.Captain.get_by_id(int(key))
          if captain:
              logging.info('got captain from key %s', key)
      if not captain:
          captain = models.Captain.all().filter('email =', email).get()
          if captain:
              logging.info('got captain from email %s', email)
      if not captain:
          logging.info('creating captain key %s name %s email %s', 
                       key, name, email)
          captain = models.Captain(name=name, email=email)

      # Over-write these values, assume volunteer database is more up to date.
      captain.name = name
      captain.email = email
      captain.phone_mobile = clean_s("Phones Mobile::number")
      captain.phone_work = clean_s("Phones Work::number")
      captain.phone_home = clean_s("Phones Home::number")
      captain.phone_fax = clean_s("Phones Fax::number")
      captain.phone_other = clean_s("Phones Other::number")
      captain.put()

      number = s["Vol Log::Project num"]
      site = models.NewSite.all().filter('number =', number).get()
      if not site:
          logging.error('site %s does not exist, skipping', number)
          continue

      query = models.SiteCaptain.all()
      query.filter('site =', site).filter('captain =', captain)
      sitecaptain = query.get()
      if sitecaptain is None:
          logging.info('Creating new SiteCaptain mapping %s to %s', 
                       site.number, captain.name)
          sitecaptain = models.SiteCaptain(site=site, captain=captain)
      # In input type is like "Volunteer Captain" but in model it's "Volunteer"
      input_type = s["Vol Log::Type"]
      for c in models.SiteCaptain.type.choices:
          if c in input_type:
              sitecaptain.type = c
              break
      sitecaptain.put()

ANNOUNCEMENT_BODY = """Please remember that your Home Depot card will be held until we receive your scope of work form.  
Thank you for serving as a captain this year!  Please use this space to include notes/correspondence with staff.
Contact RTP staff for assistance:
Cari, 650-366-6597 x224, cari@rebuildingtogetherpeninsula.org
Adam, 650-366-6597 x223, adam@rebuildingtogetherpeninsula.org
"""  
ANNOUNCEMENT_SUBJECT = """Scope of work is due March 2 for CDBG sites; all forms due March 30."""

def set_announcement():
  for s in models.NewSite.all().filter('program =', PROGRAM):
      s.announcement_subject = ANNOUNCEMENT_SUBJECT
      s.announcement_body = ANNOUNCEMENT_BODY
      s.put()
