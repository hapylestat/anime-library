

from alist.logger import alogger
from alist.config import Configuration
from flask import Flask



class Application:
  # instance store
  __me__ = None
  # set default values
  __port = 9000
  __host = "127.0.0.1"
  __debug = False
  __flask = None
  # init internal objects
  cfg = None

  @classmethod
  def get_instance(cls):
    if cls.__me__ is None:
      cls.__me__ = Application()
    return cls.__me__

  def __init__(self):
    self.cfg = Configuration.get_instance()
    self.__log = alogger.getLogger(__name__, cfg=self.cfg)
    self.__apply_settings()
    self.__flask = Flask(__name__)


  def __apply_settings(self):
    try:
      opt = self.cfg.get("server")
      log_opt = self.cfg.get("logging")


      self.__host = opt["host"]
      self.__port = int(opt["port"])
      self.__debug = bool(opt["debug"])

      # set highest log level for flask to suppress info messages
      if not log_opt["enabled"]:
        from flask import logging as flask_logging
        from logging import CRITICAL
        flask_logging.getLogger('werkzeug').setLevel(CRITICAL)

    except KeyError:
      self.__log.warning("Server settings not found (%s), use default ones", KeyError)

  def start(self):
    mode = "debug" if self.__debug else "normal"
    self.__log.info("Starting server in %s mode on %s:%s", mode, self.__host, self.__port)
    self.__flask.run(host=self.__host,
                     port=self.__port,
                     debug=self.__debug
                     )

  # Stub to pass decorator back to flask, actually doing same thing as flask decorator
  def route(self, rule, **options):
    def decorator(f):
      endpoint = options.pop('endpoint', None)
      self.__flask.add_url_rule(rule, endpoint, f, **options)
      return f
    return decorator



"""
def json_response(call, **options):
  log = alogger.getLogger(__name__)
  log.error(call.func_name)

  def new_json_response(*args, **kwargs):
    log.error("*%s" % new_json_response.call.func_name)
    return json.dumps({
      'query': call.func_name,
      'status': '',
      'data': call(*args, **kwargs),
      'cache': ''
    })

  new_json_response.call = call
  return new_json_response
"""

