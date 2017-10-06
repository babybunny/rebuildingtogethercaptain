from room.ndb_models import NewSite


def new_site_migration_add_program_model(cursor=None, num_updated=0, batch_size=100):
  """Task that handles updating the models' schema.

  This is started by
  UpdateSchemaHandler. It scans every entity in the datastore for the
  NewSite model and re-saves it so that it has the new schema fields.
  """
  