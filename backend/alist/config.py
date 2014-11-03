import os
import sys
import json
from alist.helper.singleton import Singleton

from alist.logger import alogger
import logging


@Singleton
class Configuration(object):
  location = ""
  _log = None
  _config_path = "conf/"
  _main_config = "main.json"
  _json = None

  def get_logger_path(self):
    return self.normalize_path("/tmp/alist.log")  # ToDo: avoid hardcode

  def normalize_path(self, path):
    return path.replace('/', os.path.sep)

  def __init__(self):
    self.location = os.path.dirname(os.path.abspath(__file__))
    if self.location.endswith(__package__):
      self.location = self.location[:-len(__package__)-1]
    self._config_path = self.normalize_path("%s/%s" % (self.location, self._config_path))
    self._log = alogger.getLogger(__name__, default_level=logging.DEBUG)
    self.load()

  def _load_from_configs(self, filename):
    """
     Return content of file which located in configuration directory
    """
    config_filename = "%s%s" % (self._config_path, filename)
    if os.path.exists(config_filename):
      try:
        f = open(config_filename, 'r')
        content = ''.join(f.readlines())
        f.close()
        return content
      except Exception as err:
        self._log.error("Error in opening config file: %s", err)
        raise err
    else:
      self._log.error("File not found: %s", config_filename)


  def load(self):
    """
     Load application configuration
    """
    try:
      self._json = json.loads(self._load_from_configs(self._main_config))
      self._log.info("Loaded main settings: %s", self._main_config)
      self._load_modules()
      # parse command line, currently used for re-assign settings in configuration, but can't be used as replacement
      self._load_from_commandline()
    except Exception as err:
      self._json = None
      self._log.error("Error in parsing or open config file: %s", err)
      raise err

  def _load_modules(self):
    """
    Load modules-related configuration listened in modules section
     Before loading:
      "modules": {
      "mal": "myanimelist.json",
      "ann": "animenewsnetwork.json"
     }
     After loading:
       "modules": {
        "mal": {
         ....
        },
        "ann": {
         ....
        }
      }
    """
    if self.is_exists("modules"):
      for item in self._json["modules"]:
        try:
          json_data = json.loads(self._load_from_configs(self._json["modules"][item]))
          self._json["modules"][item] = json_data
          self._log.info("Loaded module settings: %s", item)
        except Exception as err:
          self._log.error("Couldn't load module %s configuration from %s: %s",
                           item,
                           self._json["modules"][item],
                           err)

  def _load_from_commandline(self):

    def parse_one_param(param):
      self._log.debug("Parse param \'%s\' with value \'%s\'", param[0], param[2])
      keys = param[0].split('.')
      if len(keys) > 0 and keys[0] in self._json:
        item = self._json[keys.pop(0)]
        for key in keys:
          if key in item and not isinstance(item[key], (tuple, list)):
            self._log.debug("Replacing param \"%s\" to value \"%s\"",param[0],param[2])
            item[key] = param[2]
          elif key in item and isinstance(item, (tuple, list)):
            item = item[key]
          else:
            self._log.error("Couldn't recognise parameter \'%s\'", param[0])
            break
      else:
        self._log.error("Couldn't recognise parameter \'%s\'", param[0])

    args = sys.argv.copy()  # copy command line list, as we need to modify them slightly
    if len(args) >= 1:
      args.pop(0)
      self._log.info("Passed commandline arguments: %s", args)

    for param in args:
      param = param.partition('=')
      if len(param) == 3:
        parse_one_param(param)

  def is_exists(self, name):
    """
    Check for property existence
    :param name: property name
    :return:
    """
    if self._json is None:
      return False

    if name in self._json:
      return True

    return False

  def get(self, name):
    """
    Get option property
    :param name: name of the property
    :return:
    """
    #self._log.debug("Getting configuration property %s", name)
    if self._json is not None:
      try:
        return self._json[name]
      except KeyError:
        self._log.warning("Key %s not present" % name)
        raise KeyError
    else:
      return ""

  def get_module_config(self, name):
    """
     Return module configuration loaded from separate file or None
    """
    self._log.debug("Getting module configuration %s", name)
    if self.is_exists("modules"):
      if name in self._json["modules"] and not isinstance(self._json["modules"][name], str):
        return self._json["modules"][name]
    return None


