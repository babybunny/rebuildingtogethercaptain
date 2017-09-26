from google.appengine.ext import testbed
from google.appengine.ext import ndb


def activate_app_engine_testbed():
    """
    https://cloud.google.com/appengine/docs/standard/python/tools/localunittesting

    :return: activated testbed
    :rtype: google.appengine.ext.testbed
    """
    tb = testbed.Testbed()
    tb.activate()
    tb.init_datastore_v3_stub()
    tb.init_user_stub()
    tb.init_memcache_stub()
    tb.init_images_stub(enable=False)
    return tb


def clear_ndb_cache():
    """
    https://cloud.google.com/appengine/docs/standard/python/tools/localunittesting
    """
    ndb.get_context().clear_cache()
