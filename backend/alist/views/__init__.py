
"""
  General structure for view package
"""


def get_modules(path, view_extension):
  import os
  trash_files = ['__init__', '__pycache__', '__init__']
  result = []

  for root, dirs, files in os.walk(path):
    result += map(lambda x: "%s%s%s" % (
      root,
      os.sep,
      x
    ), files)

  result = map(lambda x: x[1:] if x[:1] == "." else x,  # exclude dot at start of the path
                    map(lambda x: x.replace(path, "").replace(os.sep, ".").replace(view_extension, ""),  # convert path separator to namespace sep
                        filter(lambda x: x.lower()[-len(view_extension):] == view_extension, result)  # include only files with specified extension
                        )
               )

  for exclude_item in trash_files:
    result = filter(lambda x: exclude_item not in x.split("."), result)

  return list(set(result))  # set used to exclude same items


def get_loaded_module(modules, module_name):
  module_name = module_name.split('.')  # remove alist from the top
  module_name.pop(0)
  module = modules
  try:
    while len(module_name) != 0:
      module = module.__dict__[module_name.pop(0)]
  except KeyError:
    return None

  return module

def load(allowed_views: list=None, disabled_views: list=None):
  """
  Dynamic sub-modules loading routine

  Replaces __ALL__ = [] construction and makes that automatically with logging possibility

  Compatible: Python 2.7, 3.x
  """
  import os
  import types
  from alist.logger import alogger
  from alist.config import Configuration

  view_extension = ".py"

  cfg = Configuration.get_instance()
  log = alogger.getLogger(__name__, cfg=cfg)
  mod_list = get_modules(os.path.dirname(__file__), view_extension)

  # load only allowed views
  if allowed_views is not None and len(allowed_views) != 0:
    mod_list = list(filter(lambda x: x in allowed_views, mod_list))

  # filter views from to be loaded
  if disabled_views is not None and len(disabled_views) != 0:
    mod_list = list(filter(lambda x: x not in disabled_views, mod_list))

  log.debug("Loading filtered list of views in the namespace %s: %s", __name__, mod_list)

  #  append namespace to module
  mod_list = list(map(lambda x: "%s.%s" % (__name__, x), mod_list))
  for mod in mod_list:
    module = get_loaded_module(__import__(mod, globals(), [], []), mod)
    # Call view init method if present
    if module is not None and "__init__" in module.__dict__ and isinstance(module.__dict__["__init__"], types.FunctionType):
        module.__init__()
