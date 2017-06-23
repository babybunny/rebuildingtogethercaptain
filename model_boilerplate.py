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

The way to use this module is to call the functions and then read / edit the output and 
put it in the correct file. For example, the 'routes' function produces boilerplate text for
the router in main.py.

$ python
>>> import model_boilerplate
>>> print model_boilerplate.routes('CheckRequest')

    webapp2.Route(r'/checkrequest',
                  staff.CheckRequestList,
                  name='CheckRequestList'),
    webapp2.Route(r'/checkrequest/<id:\d*>',
                  staff.CheckRequest,
                  name='CheckRequest'),

>>> 

Then copy that text into main.py.  
Search for 'example' to find the right place.

"""


import inspect
import dev_appserver
dev_appserver.fix_sys_path()
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
    """Creates js files for model and view.

    Actually writes the files in place. So be careful about overwriting your customized version.
    """
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
                            if cls._choices:
                                f.write('{0}control: "select",\n'.format(' '*(padding+4)))
                                f.write('{0}options: [\n'.format(' '*(padding+4)))
                                for choice in cls._choices:
                                    f.write('{0}{1}label: "{3}", value: "{3}"{2},\n'.format(' '*(padding+8), '{', '}', choice))
                                f.write('{0}]\n'.format(' '*(padding+4)))
                                    
                            else:
                                f.write('{0}control: "input",\n'.format(' '*(padding+4)))
                        elif issubclass(type(cls), ndb_models.ndb.DateProperty):
                            f.write('{0}control: "datepicker",\n'.format(' '*(padding+4)))
                            f.write('{0}options: {1}format: "yyyy-mm-dd"{2},\n'.format(' '*(padding+4), '{', '}'))
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
        d2g.append('{0}=mdl.{0},'.format(field))
        g2d.append('mdl.{0} = msg.{0}'.format(field))
        if (issubclass(type(cls), ndb_models.ndb.StringProperty)
            or issubclass(type(cls), ndb_models.ndb.TextProperty)
            or issubclass(type(cls), ndb_models.ndb.DateProperty)):
            message_fields.append('{0} = messages.StringField({1})'.format(field, len(message_fields) + 2))
        elif issubclass(type(cls), ndb_models.ndb.FloatProperty):
            message_fields.append('{0} = messages.FloatField({1})'.format(field, len(message_fields) + 2))
        elif issubclass(type(cls), ndb_models.ndb.IntegerProperty):
            message_fields.append('{0} = messages.IntegerField({1})'.format(field, len(message_fields) + 2))
        elif issubclass(type(cls), ndb_models.ndb.KeyProperty):
            message_fields.append('{0} = messages.IntegerField({1})'.format(field, len(message_fields) + 2))
            d2g.pop()
            d2g.append('{0}=mdl.{0}.integer_id(),'.format(field))
            g2d.pop()
            g2d.append('mdl.{0} = ndb.Key(ndb_models.{1}, msg.{0})'.format(field, cls._kind))
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


def routes(clsname):
    return """
    webapp2.Route(r'/{1}',
                  staff.{0}List,
                  name='{0}List'),
    webapp2.Route(r'/{1}/<id:\d*>',
                  staff.{0},
                  name='{0}'),
""".format(clsname, clsname.lower())
