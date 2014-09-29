import os
import json

from alist.logger import alogger
import logging

class Configuration:
  location = ""
  __log = None
  __config_path__ = "conf/"
  __main_config__ = "main.json"
  __me__ = None
  __json__ = None

  @staticmethod
  def get_logger_path():
    return Configuration.normalize_path("/tmp/alist.log")  # ToDo: avoid hardcode

  @staticmethod
  def normalize_path(path):
    return path.replace('/', os.path.sep)

  @classmethod
  def get_instance(cls):
    if cls.__me__ is None:
      cls.__me__ = Configuration()
    return cls.__me__

  def __init__(self):
    self.location = os.path.dirname(os.path.abspath(__file__))
    if self.location.endswith(__package__):
      self.location = self.location[:-len(__package__)-1]
    self.__config_path__ = Configuration.normalize_path("%s/%s" % (self.location, self.__config_path__))
    self.__log = alogger.getLogger(__name__, default_level=logging.INFO)
    self.load()

  def __load_from_configs(self, filename):
    """
     Return content of file which located in configuration directory
    """
    config_filename = "%s%s" % (self.__config_path__, filename)
    if os.path.exists(config_filename):
      try:
        f = open(config_filename, 'r')
        content = ''.join(f.readlines())
        f.close()
        return content
      except Exception as err:
        self.__log.error("Error in opening config file: %s", err)
        raise err
    else:
      self.__log.error("File not found: %s", config_filename)


  def load(self):
    """
     Load application configuration
    """
    try:
      self.__json__ = json.loads(self.__load_from_configs(self.__main_config__))
      self.__log.info("Loaded main settings: %s", self.__main_config__)
      self.__load_modules()
    except Exception as err:
      self.__json__ = None
      self.__log.error("Error in parsing or open config file: %s", err)
      raise err

  def __load_modules(self):
    if self.is_exists("modules"):
      for item in self.__json__["modules"]:
        try:
          json_data = json.loads(self.__load_from_configs(self.__json__["modules"][item]))
          self.__json__["modules"][item] = json_data
          self.__log.info("Loaded module settings: %s", item)
        except Exception as err:
          self.__log.error("Couldn't load module %s configuration from %s: %s",
                           item,
                           self.__json__["modules"][item],
                           err)

  def is_exists(self, name):
    if self.__json__ is None:
      return False

    if name in self.__json__:
      return True

    return False

  def get(self, name):
    self.__log.debug("Getting configuration property %s", name)
    if self.__json__ is not None:
      try:
        return self.__json__[name]
      except KeyError:
        self.__log.warning("Key %s not present" % name)
        raise KeyError
    else:
      return ""

  def get_module_config(self, name):
    """
     Return module configuration loaded from separate file or None
    """
    self.__log.debug("Getting module configuration %s", name)
    if self.is_exists("modules"):
      if name in self.__json__["modules"] and not isinstance(self.__json__["modules"][name], str):
        return self.__json__["modules"][name]
    return None


