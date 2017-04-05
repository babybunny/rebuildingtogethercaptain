"""Static models for use in testing.

The idea is to use this module (via remote_api_shell.py or a test URL handler)
to create a known set of models in a throwaway namespace for integration testing.

Also, these models may be used in unit tests.
"""

import datetime
from room import ndb_models

STAFFPOSITION = ndb_models.StaffPosition(
  position_name="position one",
  hourly_rate=19.19
  )

STAFF = ndb_models.Staff(
  name="Mister Staff",
  email="rebuildingtogether.rooms@gmail.com"
  )

CAPTAIN = ndb_models.Captain(
  name="Miss Captain",
  email="rebuildingtogether.capn@gmail.com",
  rooms_id="R00001",
  phone_mobile="222-333-4444",
  tshirt_size="Large",
  notes="You may say I'm a dreamer",
  last_welcome=datetime.datetime(2017, 1, 30, 1, 2, 3)
  )

PROGRAM = ndb_models.Program(
  year=2011,
  name="TEST",
  site_number_prefix="110",
  status="Active"
  )

JURISDICTION = ndb_models.Jurisdiction(
  name="FunkyTown"
  )

_KEYS = list()


def CreateAll():
  """Creates all the models in this module."""
  _KEYS.append(STAFFPOSITION.put())
  _KEYS.append(STAFF.put())
  _KEYS.append(CAPTAIN.put())
  _KEYS.append(PROGRAM.put())
  _KEYS.append(JURISDICTION.put())


def DeleteAll():
  global _KEYS
  for k in _KEYS:
    k.delete()
  _KEYS = list()

