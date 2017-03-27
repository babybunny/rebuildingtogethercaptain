"""Static models for use in testing.

The idea is to use this module (via remote_api_shell.py or a test URL handler)
to create a known set of models in a throwaway namespace for integration testing.

Also, these models may be used in unit tests.
"""

from room import ndb_models

STAFFPOSITION = ndb_models.StaffPosition(
    position_name="position one",
    hourly_rate=19.19
)

STAFF = ndb_models.Staff(
    name="Mister Staff",
    email="rebuildingtogethercaptain@gmail.com"
)

PROGRAM = ndb_models.Program(
    year=2011,
    name="TEST",
    site_number_prefix="110",
    status="Active"
)

def CreateAll():
  """Creates all the models in this module."""
  STAFFPOSITION.put()
  STAFF.put()
  PROGRAM.put()
