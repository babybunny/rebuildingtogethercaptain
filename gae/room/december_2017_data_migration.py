"""
ref: https://cloud.google.com/appengine/articles/update_schema
"""

import webapp2
from google.appengine.ext import ndb
from google.appengine.ext import deferred

from gae.room import ndb_models

program_type_cache = {}
program_cache = {}


class December2017Migration(webapp2.RequestHandler):

  BATCH_SIZE = 100
  PROGRAM_TOKEN_ATTR = 'program'
  PROGRAM_KEY_ATTR = 'program_key'

  def post(self):
    deferred.defer(self.update())
    self.response.write("""
        Schema update started. Check the console for task progress.
        <a href="/">View entities</a>.
        """)

  # exposed for testing
  def update(self):
    self._migrate(ndb_models.NewSite)
    self._migrate(ndb_models.Order)
    self._migrate(ndb_models.CheckRequest)
    self._migrate(ndb_models.Expense)
    self._migrate(ndb_models.StaffTime)
    self._migrate(ndb_models.VendorReceipt)
    
  def _migrate(self, model_type, cursor=None):
    query = model_type.query()
    results, next_cursor, more = query.fetch_page(December2017Migration.BATCH_SIZE, start_cursor=cursor)
    to_put = []
    for result in results:
      program = self._parse_program_from_program_token_string(getattr(result, December2017Migration.PROGRAM_TOKEN_ATTR))
      if program is not None:
        setattr(result, December2017Migration.PROGRAM_KEY_ATTR, program.key)
        to_put.append(result)

    to_put and ndb.put_multi(to_put)
    more and deferred.defer(obj=self._migrate, model_type=model_type, cursor=next_cursor)

  def _parse_program_from_program_token_string(self, program_token):
    """program_token is like 2017 NRD"""
    try:
      key = ndb.Key(ndb_models.Program, program_token)
      program = key.get()
      if program is None:
        program_string_split = program_token.split()
        assert len(program_string_split) == 2
        year_string, program_type_string = program_string_split
        year = int(year_string)
        program_type = program_type_cache.get(program_type_string)
        if program_type is None:
          program_type = ndb_models.ProgramType.get_or_create(program_type_string)
          program_type_cache[program_type_string] = program_type
        program_key = (program_type_string, year)
        program = program_cache.get(program_key)
        if program is None:
          program, _ = ndb_models.Program.get_or_create(program_type.key, year)
          program_cache[program_key] = program
        return program
    except:
      return None
