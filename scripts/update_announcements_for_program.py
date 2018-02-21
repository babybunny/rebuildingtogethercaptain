import os
import time
import logging
from argparse import ArgumentParser

from gae.room import ndb_models


class UpdateAnnouncements(object):

  def __init__(self):
    p = ArgumentParser()
    p.add_argument('-p', '--program-type-name', help="eg. NRD", required=True)
    p.add_argument('-y', '--year', help="eg 2018", required=True, type=int)
    p.add_argument('-s', '--subject', help="New announcement subject text", required=True)
    p.add_argument('-i', '--input-path', help="path to file with new announcement text", required=True)
    p.add_argument('-f', '--force', help="no interactive prompts", action='store_true')
    args = p.parse_known_args()
    self.program_type_name = args.program_type_name
    self.year = args.year
    self.input_path = args.input_path
    self.force = args.force
    self.new_announcement_subject = args.subject
    self.new_announcement_body = None
    self.program_type = None
    self.program = None
    self.sites = None  # type: list[ndb_models.NewSite]
    self.site_count = None

  def go(self):
    self._validate_and_process_args()
    self._confirm_interactively_then_continue()

  def _confirm_interactively_then_continue(self):
    if not self.force:
      ans = None
      while ans not in ('y', 'n', 'yes', 'no'):
        ans = raw_input("About to update announcement for {} sites. Proceed? ").lower()
      if ans.startswith("n"):
        return
    idx = 1
    s = time.time()
    for site in self.sites:
      site.announcement_subject = self.new_announcement_subject
      site.announcement_body = self.new_announcement_body
      site.put()
      if time.time() - s > 3:
        s = time.time()
        logging.info("{}% Complete".format(round(float(idx * 100)/self.site_count, 2)))
      idx += 1

  def _validate_and_process_args(self):
    if not os.path.isfile(self.input_path):
      raise SystemExit("Could not find file {}".format(self.input_path))
    elif not os.access(self.input_path, os.R_OK):
      raise SystemExit("File {} cannot be read".format(self.input_path))

    with open(self.input_path) as io:
      self.new_announcement_body = io.read()

    self.program_type = ndb_models.ProgramType.query(name=self.program_type_name).get()
    if not self.program_type:
      logging.error("{} is not a valid program type".format(self.program_type_name))
      logging.error("Valid program types are")
      for pt in ndb_models.ProgramType.query():
        logging.error("  {}".format(pt.name))
      raise SystemExit("{} is not a valid program type".format(self.program_type_name))

    self.program = ndb_models.Program.query(
      ndb_models.Program.program_type == self.program_type.key,
      ndb_models.Program.year == self.year
    ).get()
    if not self.program:
      raise SystemExit("Could not find a {} program for the year {}".format(self.program_type, self.year))

    self.sites = ndb_models.NewSite.query(ndb_models.NewSite.program_key == self.program.key)
    self.site_count = self.sites.count()
    if not self.site_count:
      raise SystemExit("No sites found for {} {}".format(self.year, self.program_type))