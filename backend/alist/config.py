__author__ = 'lestat'

import os
import json
from logger import alogger


class Configuration:
  location = ""
  log = None
  __config_path__ = "conf/main.json"
  __me__ = None
  __json__ = None

  @staticmethod
  def getLoggerPath():
    return "/tmp/alist.log"

  @classmethod
  def getInstance(cls):
    if cls.__me__ is None:
      cls.__me__ = Configuration()
    return  cls.__me__

  def __init__(self):
    self.location = os.path.dirname(os.path.abspath(__file__))
    if self.location.endswith(__package__):
      self.location = self.location[:-len(__package__)-1]
    self.__config_path__ = "%s/%s" % (self.location, self.__config_path__)
    self.log =  alogger.getLogger(__name__)
    self.load()

  def load(self):
    """
     Load application configuration
    """
    if os.path.exists(self.__config_path__):
      try:
        file = open(self.__config_path__, 'r')
        self.__json__ = json.loads(file.readall())
        file.close()
      except Exception:
        self.__json__ = None
        self.log.error("Error in parsing or open config file: %s" % Exception.message)
    else:
      self.log.error("Couldn't read config file %s" % self.__config_path__)



    pass


