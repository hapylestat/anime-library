
import sys
import logging
from os import environ


#from logging.handlers import RotatingFileHandler

class alogger:

  @staticmethod
  def getLogger(name, cfg=None, default_level=None):
    is_enabled = True
    log = logging.getLogger(name)
    handlers = alogger.getHandlers()

    if cfg is None and default_level is not None:
      log.setLevel(default_level)

    try:
      if cfg is not None:
        log_cfg = cfg.get("logging")
        alogger.setLogLevel(log, log_cfg["log_level"])
        is_enabled = log_cfg["enabled"]
    except KeyError:
      pass

    # hack, print logs only for reloaded thread
    if environ.get('WERKZEUG_RUN_MAIN') != 'true':
      is_enabled = False

    if is_enabled:
      for handler in handlers:
        log.addHandler(handler)
    else:
      log.addHandler(logging.NullHandler())

    return log

  @staticmethod
  def getHandlers():
    new_format = logging.Formatter('%(levelname)s %(asctime)s %(filename)s:%(lineno)d - %(message)s')
    handlers = [

    # output error handler
    logging.StreamHandler(sys.stderr)

    # uncomment to allow file output handler
    # RotatingFileHandler(cfg.getLoggerPath(), "a")

    ]
    # assign same format output to handler
    for item in handlers:
      item.setFormatter(new_format)

    return handlers

  @staticmethod
  def setLogLevel(log, level):
    if level.lower().strip() == "info":
      log.setLevel(logging.INFO)
    elif level.lower().strip() == "critical":
      log.setLevel(logging.CRITICAL)
    elif level.lower().strip() == "error":
      log.setLevel(logging.ERROR)
    elif level.lower().strip() == "debug":
      log.setLevel(logging.DEBUG)
    elif level.lower().strip() == "warning":
      log.setLevel(logging.WARNING)
    else:
      log.setLevel(logging.NOTSET)
