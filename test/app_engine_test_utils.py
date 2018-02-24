from google.appengine.ext import ndb
from google.appengine.ext import testbed


def activate_app_engine_testbed_and_clear_cache():
  """
  https://cloud.google.com/appengine/docs/standard/python/tools/localunittesting

  :return: activated testbed
  :rtype: google.appengine.ext.testbed
  """
  tb = testbed.Testbed()
  tb.activate()
  tb.init_datastore_v3_stub()
  tb.init_search_stub()
  tb.init_user_stub()
  tb.init_blobstore_stub()
  tb.init_memcache_stub()
  tb.init_images_stub(enable=False)
  ndb.get_context().clear_cache()
  return tb
