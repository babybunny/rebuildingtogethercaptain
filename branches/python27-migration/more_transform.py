"""More bulkloader transforms.  

See http://googleappengine.googlecode.com/svn/trunk/python/google/appengine/ext/bulkload/transform.py
"""

from google.appengine.api import datastore

def create_optional_foreign_key(kind, key_is_id=False):
  """Like transform.create_foreign_key, but handles empty inputs."""

  def generate_foreign_key_lambda(value):
    if value is '':
        return None
    if key_is_id:
      value = int(value)
    return datastore.Key.from_path(kind, value)

  return generate_foreign_key_lambda


def regexp_optional_bool(regexp, flags=0):
  """Return a boolean if the expression matches with re.match.

  Note that re.match anchors at the start but not end of the string.

  Args:
    regexp: String, regular expression.
    flags: Optional flags to pass to re.match.

  Returns:
    Method which returns a Boolean if the expression matches.
  """

  def transform_function(value):
    if value is None:
      return False
    return bool(re.match(regexp, value, flags))

  return transform_function
