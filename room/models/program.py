import logging

from google.appengine.ext import ndb


class Program(ndb.Model):
  """Identifies a program like "National Rebuilding Day".

  Programs with status 'Active' will be visible to Captains.

  Keys are shorthand like "2012 NRD".
  """
  year = ndb.IntegerProperty()
  name = ndb.StringProperty()
  site_number_prefix = ndb.StringProperty()
  status = ndb.StringProperty(choices=('Active', 'Inactive'), default='Inactive')

  @staticmethod
  def from_site_number(program_number):
    year = '20' + program_number[0:2]
    mode = program_number[2]
    program = None
    if mode == '0':
      program = year + ' NRD'
    elif mode == '1':
      program = year + ' NRD'
    elif mode == '3':
      program = year + ' Misc'
    elif mode == '5':
      program = year + ' Safe'
    elif mode == '6':
      program = year + ' Safe'
    elif mode == '7':
      program = year + ' Energy'
    elif mode == '8':
      program = year + ' Teambuild'
    elif mode == '9':
      program = year + ' Youth'
    elif mode == 'Z':
      program = year + ' Test'
    else:
      logging.warn('no program for site number %s', program_number)
    return program