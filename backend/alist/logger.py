
import sys
from flask import logging
from logging import Formatter
#from logging.handlers import RotatingFileHandler



class alogger:

  @staticmethod
  def getLogger(name):
    log = logging.getLogger(name)
    handlers = alogger.getHandlers()
    for handler in handlers:
      log.addHandler(handler)
    return log

  @staticmethod
  def getHandlers():
    format = Formatter('%(levelname)s %(asctime)s %(filename)s:%(lineno)d - %(message)s')

    sh = logging.StreamHandler(sys.stderr)
    #rfh = RotatingFileHandler(cfg.getLoggerPath(), "a")

    #rfh.setFormatter(format)
    sh.setFormatter(format)
    return [
     #        rfh,
             sh
    ]

