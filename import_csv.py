"""
Imports site and captain data into ROOMS for a NRD batch data upload. "NRD" is hard-coded.

Intended to be run with the remote_api. Great instructions at
https://github.com/babybunny/rebuildingtogethercaptain/wiki/Import-Site-and-Captain-Data

# or for development..
bash> python $(which remote_api_shell.py) -s localhost:8081
dev~rebuildingtogethercaptain> reload(import_csv)
<module 'import_csv' from '/Users/babybunny/appengine/rebuildingtogethercaptain/import_csv.py'>
dev~rebuildingtogethercaptain> import_csv.import_sites(input_csv="../2012_ROOMS_site_info_sample.csv")
dev~rebuildingtogethercaptain> import_csv.import_captains(input_csv="../2012_ROOMS_Captain_email_sample.csv")
"""

import csv
import sys
import logging

from gae.room import ndb_models


def clean_get(d, k):

  ### bit of dirty data coverage ###
  ok = k
  if k not in d:
    k = k.replace("Repair Application: ", "")
    if k not in d:
      k = "Repair Application: " + k
      if k not in d:
        raise KeyError("No column named \"{}\"".format(ok))
  ### bit of dirty data coverage ###

  return d[k].replace('\n', ' ').replace('\xe2', "'").replace('\x80', "'").replace('\x99', '').replace('\xc3',
                                                                                                       '').replace(
    '\x95', '').encode('ascii', 'replace')


def get_program(year):
  nrd_type, created = ndb_models.ProgramType.get_or_create("NRD")
  program, created = ndb_models.Program.get_or_create(nrd_type.key, int(year))
  return program


def sanity_check_headers(e, a, path):
  if e != a:
    for h in e - a:
      print >> sys.stderr, "Expected header \"{}\" was not found in {}".format(h, path)
    for h in a - e:
      print >> sys.stderr, "Found header \"{}\" in {} which was not expected".format(h, path)
    sys.stderr.flush()
    raise SystemExit(1)


def import_sites(input_csv):
  """
  input_csv is a path like "../2012_ROOMS_site_info_sample.csv"
  """
  expected_headers = {"Program Year", "Announcement Subject", "Announcement Body", "Site ID",
                      "Budgeted Cost in Campaign", "Repair Application: Applicant's Name", "Applicant Home Phone",
                      "Applicant Mobile Phone", "Applicant Work Phone", "Recipient's Street Address",
                      "Recipient's City", "Recipient's Zip Code", "Jurisdiction", "Sponsor",
                      "Repair Application: RRP Test Results", "Photos Link"}
  reader = csv.DictReader(open(input_csv))
  actual_headers = set(reader.fieldnames)
  sanity_check_headers(expected_headers, actual_headers, input_csv)
  for s in reader:
    number = s["Site ID"]
    site = ndb_models.NewSite.query(ndb_models.NewSite.number == number).get()
    if site:
      logging.info('site %s exists, skipping', number)
      continue
    else:
      site = ndb_models.NewSite(number=number)
    program = get_program(s['Program Year'])
    site.program = program.name
    site.program_key = program.key
    budget = s.get("Budgeted Cost in Campaign", "$0").strip("$").replace(",", "").replace(".00", "") or '0'
    site.budget = int(budget)
    site.name = clean_get(s, "Repair Application: Applicant's Name")
    site.street_number = clean_get(s, "Recipient's Street Address")
    site.city_state_zip = "%s CA, %s" % (
      clean_get(s, "Recipient's City"),
      clean_get(s, "Recipient's Zip Code"))
    site.applicant = clean_get(s, "Repair Application: Applicant's Name")
    site.applicant_home_phone = clean_get(s, 
      "Repair Application: Applicant Home Phone")
    site.applicant_work_phone = clean_get(s, 
      "Repair Application: Applicant Work Phone")
    site.applicant_mobile_phone = clean_get(s, 
      "Repair Application: Applicant Mobile Phone")
    site.sponsor = clean_get(s, "Sponsor")
    site.rrp_test = clean_get(s, "Repair Application: RRP Test Results")
    site.rrp_level = clean_get(s, "Repair Application: RRP Test Results")
    # site.roof = clean_get(s, "Roof?")
    site.jurisdiction = clean_get(s, "Jurisdiction")
    site.announcement_subject = clean_get(s, "Announcement Subject")
    site.announcement_body = clean_get(s, "Announcement Body")
    site.put()
    logging.info('put site %s', number)


def import_captains(input_csv):
  """
  input_csv is a path like "../2012_ROOMS_site_info_sample.csv"
  """
  expected_headers = {"Site ID", "Name", "ROOMS Captain ID", "Phone", "Email", "Project Role"}
  reader = csv.DictReader(open(input_csv))
  actual_headers = set(reader.fieldnames)
  sanity_check_headers(expected_headers, actual_headers, input_csv)
  for s in reader:
    key = s.get('key')
    email = clean_get(s, "Email")
    rooms_id = clean_get(s, "ROOMS Captain ID")
    name = clean_get(s, "Name")
    captain = None
    if key:
      captain = ndb_models.Captain.get_by_id(int(key))
      if captain:
        logging.info('got captain from key %s', key)
    if not captain:
      captain = ndb_models.Captain.query(ndb_models.Captain.rooms_id == rooms_id).get()
      if captain:
        logging.info('got captain from rooms_id %s', rooms_id)
    if not captain:
      captain = ndb_models.Captain.query(ndb_models.Captain.email == email).get()
      if captain:
        logging.info('got captain from email %s', email)
    if not captain:
      logging.info('creating captain key %s name %s email %s rooms_id %s',
                   key, name, email, rooms_id)
      captain = ndb_models.Captain(name=name, email=email, rooms_id=rooms_id)

    # Over-write these values, assume volunteer database is more up to
    # date.
    captain.name = name
    captain.email = email
    captain.rooms_id = rooms_id
    captain.put()

    numbers = [n.strip() for n in s["Site ID"].split(',')]
    for number in numbers:
      site = ndb_models.NewSite.query(ndb_models.NewSite.number == number).get()
      if not site:
        logging.error('site %s does not exist, skipping', number)
        continue

      # In input type is like "Volunteer Captain" but in model it's
      # "Volunteer"
      input_type = s.get("Captain Type", s.get("Project Role"))
      for t in ndb_models.SiteCaptain.type._choices:
        if t in input_type:
          break

      query = ndb_models.SiteCaptain.query(ndb_models.SiteCaptain.site == site.key).filter(ndb_models.SiteCaptain.captain == captain.key)
      sitecaptain = query.get()
      if sitecaptain is None:
        logging.info('Creating new SiteCaptain mapping %s to %s',
                     site.number, captain.name)
        sitecaptain = ndb_models.SiteCaptain(site=site.key, captain=captain.key, type=t)
      else:
        logging.info('Found existing SiteCaptain')
        sitecaptain.type = t
      sitecaptain.put()
