"""
Imports site and captain data into ROOM.  
Intended to be run with the remote_api:
bash> export PYTHONPATH=.:$PYTHONPATH
bash> python $(which remote_api_shell.py) -s rebuildingtogethercaptain.appspot.com
s~rebuildingtogethercaptain-hrd> import import_csv

Great instructions at
https://code.google.com/p/rebuildingtogethercaptain/issues/detail?id=181

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

PROGRAM = '2014 NRD'
# PROGRAM = '2014 Safe'

def import_sites(input_csv="../2012_ROOMS_site_info_sample.csv"):
    """Change input_csv to actual input file - the default is test data."""
    reader = csv.DictReader(open(input_csv))
    for s in reader:
      number = s["Number"]
      site = models.NewSite.all().filter('number =', number).get()
      if site:
          logging.info('site %s exists, skipping', number)
          continue
      else:
          site = models.NewSite(number=number)
      site.program = PROGRAM
      # site.budget = int(s["Budget"])

      def clean_s(k):
          return s[k].replace('\n', ' ').replace('\xe2', "'").replace('\x80', "'").replace('\x99', '').encode('ascii', 'replace')

      site.name = clean_s("Recipient Name")
      site.street_number = clean_s("Street Number")
      site.city_state_zip = "%s CA, %s" % (
          clean_s("City"), clean_s("Zip"))
      site.applicant_home_phone = clean_s("Applicant Home Phone")
      site.applicant_work_phone = clean_s("Applicant Work Phone: ")
      site.applicant_mobile_phone = clean_s("Applicant Mobile Phone:")
      # site.applicant_email = clean_s("Applicant email")
      # site.sponsor = clean_s("Sponsor")
      # site.rating = clean_s("TODO")
      # site.rrp_test = clean_s("TODO RRP Is_Testing Required")
      # site.rrp_level = clean_s("TODO RRP Level")
      # site.roof = clean_s("TODO Roof_Request_Professional_Evaluation")
      # site.jurisdiction = clean_s("Jurisdiction")
      site.put()
      logging.info('put site %s', number)

def import_captains(input_csv="../2012_ROOMS_Captain_email_sample.csv"):
    """Change input_csv to actual input file - the default is test data."""
    reader = csv.DictReader(open(input_csv))
    for s in reader:
      def clean_s(k):
          return s[k].replace('\n', ' ').replace('\xe2', "'").replace('\x80', "'").replace('\x99', '').encode('ascii', 'replace')

      key = s.get('key')
      name = "%s %s" % (clean_s("First Name"),
                        clean_s("Last Name"))
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
      captain.phone_mobile = clean_s("Phone mobile")
      captain.phone_work = clean_s("Phone work")
      captain.phone_home = clean_s("Phone home")
      # captain.phone_fax = clean_s("Phones Fax::number")
      # captain.phone_other = clean_s("Phones Other::number")
      captain.put()

      number = s["Number"]
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
      input_type = s["Role"]
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

# SAH
ANNOUNCEMENT_SUBJECT = """Thank you for your help with SAH!"""
ANNOUNCEMENT_BODY = ''

# NRD 2014 
ANNOUNCEMENT_BODY = """
Thank you for serving as a captain this year!  Please use this space to include 
notes/correspondence with staff.                                                 
Contact RTP staff for assistance:                                                
Roger, 650-366-6597 x227, roger@rebuildingtogetherpeninsula.org
Adam, 650-366-6597 x223, adam@rebuildingtogetherpeninsula.org                    
"""
ANNOUNCEMENT_SUBJECT = """Scope of work is due March 5; all forms due March 28."""

def set_announcement():
  for s in models.NewSite.all().filter('program =', PROGRAM):
      s.announcement_subject = ANNOUNCEMENT_SUBJECT
      s.announcement_body = ANNOUNCEMENT_BODY
      s.put()
