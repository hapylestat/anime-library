

class Singleton:

  def __init__(self, decorated):
    self._decorated = decorated

  def get_instance(self):
    if '_instance' in dir(self):
      return self._instance
    else:
      self._instance = self._decorated()
      return self._instance

  def __call__(self):
    raise TypeError('Singletons must be accessed through `get_instance()`.')

  def __instancecheck__(self, inst):
    return isinstance(inst, self._decorated)
