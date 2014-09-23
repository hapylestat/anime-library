import os
import json

from alist.logger import alogger


class Configuration:
  location = ""
  log = None
  __config_path__ = "conf/main.json"
  __me__ = None
  __json__ = None

  @staticmethod
  def get_logger_path():
    return Configuration.normalize_path("/tmp/alist.log")

  @staticmethod
  def normalize_path(path):
    return path.replace('/', os.path.sep)

  @classmethod
  def get_instance(cls):
    if cls.__me__ is None:
      cls.__me__ = Configuration()
    return  cls.__me__

  def __init__(self):
    self.location = os.path.dirname(os.path.abspath(__file__))
    if self.location.endswith(__package__):
      self.location = self.location[:-len(__package__)-1]
    self.__config_path__ = Configuration.normalize_path("%s/%s" % (self.location, self.__config_path__))
    self.log =  alogger.getLogger(__name__)
    self.load()

  def load(self):
    """
     Load application configuration
    """
    if os.path.exists(self.__config_path__):
      try:
        file = open(self.__config_path__, 'r')
        self.__json__ = json.loads(''.join(file.readlines()))
        file.close()
      except Exception as err:
        self.__json__ = None
        self.log.error("Error in parsing or open config file: %s", err)
    else:
      self.log.error("Couldn't read config file %s", self.__config_path__)

  def get(self, name):
    self.log.debug("Getting configuration property %s", name)
    if self.__json__ is not None:
      return self.__json__[name]
    else:
      return ""



