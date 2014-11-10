
"""
  General structure for view package
"""

def load():
  """
  Dynamic sub-modules loading routine

  Replaces __ALL__ = [] construction and makes that automatically with logging possibility

  Compatible: Python 2.7, 3.x
  """
  import os
  from alist.logger import alogger
  from alist.config import Configuration

  log = alogger.getLogger(__name__, cfg=Configuration.get_instance())
  mods = []
  mod_list = os.listdir(os.path.dirname(__file__))
  log.debug("List of available modules in namespace %s found: %s", __name__, mod_list)

  for i in mod_list:
    mods.append("%s.%s" % (__name__, i.split('.')[0]))

  mod_list = list(set(mods))

  # remove system and unused modules, possibility to add filter
  mod_list.remove('%s.__init__' % __name__)
  mod_list.remove('%s.__pycache__' % __name__)

  log.debug("Loading filtered list of views in the namespace %s: %s", __name__, mod_list)

  for mod in mod_list:
    __import__(mod, globals(), locals(), [], 0)

