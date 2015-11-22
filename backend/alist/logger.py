
import sys
import logging
from os import environ

from logging.handlers import RotatingFileHandler

CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0

_levelToName = {
  CRITICAL: 'CRITICAL',
  ERROR: 'ERROR',
  WARNING: 'WARNING',
  INFO: 'INFO',
  DEBUG: 'DEBUG',
  NOTSET: 'NOTSET',
  }

_nameToLevel = {
  'CRITICAL': CRITICAL,
  'ERROR': ERROR,
  'WARN': WARNING,
  'WARNING': WARNING,
  'INFO': INFO,
  'DEBUG': DEBUG,
  'NOTSET': NOTSET,
  }

class alogger:

  @staticmethod
  def getLogger(name: str, cfg=None, default_level=None):
    _log_options = {  # default log options
      "log_level": default_level if default_level is not None else "debug",
      #  enable logging by default if configuration or default log level is set
      "enabled": cfg is not None or default_level is not None,
      #  Output log to tty if logging is possible
      "tty": True and (cfg is not None or default_level is not None)
    }

    flask_reload = True
    log = logging.getLogger(name)

    if cfg is not None:
      alogger.setLogLevel(log, cfg.get("logging.log_level", default=_log_options["log_level"], check_type=str))
      flask_reload = not cfg.get("server.debug.external_debug", default=not flask_reload, check_type=bool)
      _log_options["file"] = cfg.get("logging.file", default="", check_type=str)
    else:
      # set log level for the instance from default one passed in case, if no configuration available
      _log_options["log_level"] is not None and alogger.setLogLevel(log, _log_options["log_level"])

    # hack, print logs only for reloaded thread
    if flask_reload and environ.get('WERKZEUG_RUN_MAIN') != 'true':
      _log_options["enabled"] = False

    for handler in alogger.getHandlers(_log_options):
      log.addHandler(handler)

    return log

  @staticmethod
  def getHandlers(options: dict):
    new_format = logging.Formatter('%(levelname)s %(asctime)s %(filename)s:%(lineno)d - %(message)s')
    handlers = []

    # return Null handler if logging is not allowed
    if "enabled" in options and not options["enabled"]:
      handlers.append(logging.NullHandler())
      return handlers

    # output error handler
    if "tty" in options and options["tty"]:
     handlers.append(logging.StreamHandler(sys.stderr))

    if "file" in options and options["file"].strip() != "":
      # uncomment to allow file output handler
      handlers.append(RotatingFileHandler(options["file"], "a"))

    # assign same format output to handlers
    for item in handlers:
      item.setFormatter(new_format)

    return handlers

  @staticmethod
  def setLogLevel(log, level):
    level = level.upper().strip()
    if level in _nameToLevel:
      log.setLevel(_nameToLevel[level])
    else:
      log.setLevel(NOTSET)


