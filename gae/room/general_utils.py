
def get_all_subclasses(clazz):
  subclasses = []
  for subclass in clazz.__subclasses__():
    subclasses.append(subclass)
    subclasses.extend(get_all_subclasses(subclass))
  return subclasses
