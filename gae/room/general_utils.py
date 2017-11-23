
def get_all_subclasses(clazz):
  subclasses = []
  for subclass in clazz.__subclasses__():
    subclasses.append(subclass)
    subclasses.extend(get_all_subclasses(subclass))
  return subclasses


def delete_all_in_index(index):
  """
  copied from https://cloud.google.com/appengine/docs/standard/python/search
  """
  # index.get_range by returns up to 100 documents at a time, so we must
  # loop until we've deleted all items.
  while True:
    # Use ids_only to get the list of document IDs in the index without
    # the overhead of getting the entire document.
    document_ids = [
      document.doc_id
      for document
      in index.get_range(ids_only=True)]

    # If no IDs were returned, we've deleted everything.
    if not document_ids:
      break

    # Delete the documents for the given IDs
    index.delete(document_ids)
