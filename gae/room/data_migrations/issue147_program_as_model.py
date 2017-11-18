import datetime

from gae.room import ndb_models


PROGRAMS = {
    'Energy': [2011, 2012, 2013, 2014, 2015, 2016],
    'Misc': [2011, 2012, 2013, 2014, 2015, 2016],
    'NRD': [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018],
    'Safe': [2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018],
    'Teambuild': [2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018],
    'Test': [2011],
    'Youth': [2011, 2012, 2013, 2014, 2015, 2016],
}


def create_programs():
  programs = []
  assert not ndb_models.ProgramType.query().get()
  for program_type_name, years in PROGRAMS.items():
    program_type, created = ndb_models.ProgramType.get_or_create(program_type_name)
    assert created
    program_type_key = program_type.key
    for year in years:
      status = ndb_models.Program.INACTIVE_STATUS
      if year >= datetime.datetime.now().year:
        status = ndb_models.Program.ACTIVE_STATUS
      program, created = ndb_models.Program.get_or_create(
        program_type_key=program_type_key,
        year=year,
        status=status
      )
      assert created
      programs.append(program)
  return programs


def get_all_programs():
  return ndb_models.Program.query().fetch() or create_programs()
