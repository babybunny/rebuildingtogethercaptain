"""Notes and helpers for creating boilerplate code for models.

We have a lot of models and each one has some boilderplate in 
app/js/models
app/js/views
wsgi_service.py
main.py
staff.py

Some of this repetition can be removed but at risk of getting too "meta" 
and hard to follow. I find that having some level of repetition is acceptable 
(DRY principle is not absolute) as long as there are tools to manage it.
"""


import inspect
from room import ndb_models

ALIAS = {'NewSite': 'Site'}  # using 'Site' from now on.

ndb_model_classes = dict(
    (k, v)
    for k, v in ndb_models.__dict__.items()
    if inspect.isclass(v) and issubclass(v, ndb_models.ndb.Model))


def label(s):
    """Return a string formatted as a label for s."""
    return s.replace('_', ' ').capitalize()


def js(clsname):
    """Creates js files for model and view."""
    wsgi_path_fragment = clsname.lower()
    with open('app/js/models/{}.js'.format(wsgi_path_fragment), 'w') as f, open('app/js/models/example.js', 'r') as examplef:
        for line in examplef:
            line = line.replace('example', wsgi_path_fragment)
            f.write(line)
            
    with open('app/js/views/{}.js'.format(wsgi_path_fragment), 'w') as f, open('app/js/views/example.js', 'r') as examplef:
        for line in examplef:
            line = line.replace('example', wsgi_path_fragment)                
            f.write(line)
            if '// boilerplate' in line:
                padding = line.find('/')
                # expand the model's fields
                for field, cls in ndb_model_classes[clsname].__dict__.items():
                    if not inspect.isclass(type(cls)): continue
                    if issubclass(type(cls), ndb_models.ndb.Property):
                        f.write('{0}{1}\n'.format(' '*padding, '{'))
                        f.write('{0}name: "{1}",\n'.format(' '*(padding+4), field))
                        f.write('{0}label: "{1}",\n'.format(' '*(padding+4), label(field)))
                        if (issubclass(type(cls), ndb_models.ndb.StringProperty)
                              or issubclass(type(cls), ndb_models.ndb.IntegerProperty)
                              or issubclass(type(cls), ndb_models.ndb.FloatProperty)):
                            f.write('{0}control: "input",\n'.format(' '*(padding+4)))
                        elif issubclass(type(cls), ndb_models.ndb.TextProperty):
                            f.write('{0}control: "textarea",\n'.format(' '*(padding+4)))
                        elif issubclass(type(cls), ndb_models.ndb.BlobProperty):
                            f.write('{0}// "{1} is a BlobProperty, skipping",\n'.format(' '*(padding), field))
                        elif issubclass(type(cls), ndb_models.ndb.KeyProperty):
                            f.write('{0}// "{1} is a Key.  TODO",\n'.format(' '*(padding+4), field))
                        else:
                            f.write('{0}// "{1} is a {2}.  TODO",\n'.format(' '*(padding+4), field, str(cls)))
                        f.write('{0}{1}\n'.format(' '*padding, '},'))
                        
def api(clsname):
    message_fields = []
    d2g = []
    g2d = []

    for field, cls in ndb_model_classes[clsname].__dict__.items():
        if not inspect.isclass(type(cls)): continue
        if not issubclass(type(cls), ndb_models.ndb.Property): continue
        d2g.append('{0}=mdl.{0}'.format(field))
        g2d.append('mdl.{0} = msg.{0}'.format(field))
        if issubclass(type(cls), ndb_models.ndb.StringProperty):
            message_fields.append('{0} = messages.StringField({1})'.format(field, len(message_fields) + 2))
        elif issubclass(type(cls), ndb_models.ndb.FloatProperty):
            message_fields.append('{0} = messages.FloatField({1})'.format(field, len(message_fields) + 2))
        elif (issubclass(type(cls), ndb_models.ndb.IntegerProperty)
              or issubclass(type(cls), ndb_models.ndb.KeyProperty)):
            message_fields.append('{0} = messages.IntegerField({1})'.format(field, len(message_fields) + 2))
        else:
            d2g.pop()
            g2d.pop()
    return """
############
# {0} #
############

def _{0}ModelToMessage(mdl):
  s = {0}(
    id=mdl.key.integer_id(),
    {2}
  )
  # any special handling, like for user objects or datetimes
  return s

def _{0}MessageToModel(msg, mdl):
  {3}
  # can't set automatic fields:
  # TODO
  return mdl

class {0}(messages.Message):
  id = messages.IntegerField(1)
  {1}



#  ({0}, ndb_models.{0},
# _{0}MessageToModel, _{0}ModelToMessage),

    """.format(clsname,
               '\n  '.join(message_fields),
               '\n    '.join(d2g),
               '\n  '.join(g2d))


def views(clsname):
    return """
class {0}List(StaffHandler):
  def get(self):
    return _EntryList(self.request, ndb_models.{0}, '{1}_list')

class {0}(EditView):
  model_class = ndb_models.{0}
  list_view = '{0}List'
  template_value = '{1}'
  template_file = 'simple_form'
""".format(clsname, clsname.lower())

