from google.appengine.api import search
from google.appengine.ext import deferred


def get_all_subclasses(clazz):
  subclasses = []
  for subclass in clazz.__subclasses__():
    subclasses.append(subclass)
    subclasses.extend(get_all_subclasses(subclass))
  return subclasses


def index_blob(text_blob, index_name, supplemental_fields=None, document_id=None):
  """
  :param blob: blob of text to index
  :param index_name: name of index
  :param supplemental_fields: optional list of search fields to add to blob
  :param document_id: optional string to use as id for document
  """
  index = search.Index(name=index_name)
  fields = supplemental_fields or []
  fields.append(search.TextField(name='blob', value=text_blob))
  doc = search.Document(doc_id=document_id, fields=fields)
  index.put(doc)
  return doc


def index_blob_async(text_blob, index_name, supplemental_fields=None, document_id=None):
  """
  Asynchronous version of index_blob

  :param blob: blob of text to index
  :param index_name: name of index
  :param supplemental_fields: optional list of search fields to add to blob
  :param document_id: optional string to use as id for document
  :returns: taskqueue.Task
  """
  return deferred.defer(
    obj=index_blob,
    text_blob=text_blob,
    index_name=index_name,
    supplemental_fields=supplemental_fields,
    document_id=document_id)
