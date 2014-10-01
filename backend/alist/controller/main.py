from alist.helper.singleton import Singleton
from alist.logger import alogger
from alist.config import Configuration
from flask import Flask
import json


@Singleton
class Application(object):
  # set default values
  _settings = {
    "port": 9000,
    "host": "127.0.0.1",
    "debug": False,
    "debug_level": 0
  }

  _flask = None
  # init internal objects
  cfg = None

  def __init__(self):
    self.cfg = Configuration.get_instance()
    self._log = alogger.getLogger(__name__, cfg=self.cfg)
    self._apply_settings()
    self._flask = Flask(__name__)


  def _apply_settings(self):
    try:
      opt = self.cfg.get("server")
      log_opt = self.cfg.get("logging")

      self._settings["host"] = opt["host"]
      self._settings["port"] = int(opt["port"])
      self._settings["debug"] = bool(opt["debug"])
      self._settings["debug_level"] = int(opt["debug_level"])

      # set highest log level for flask to suppress info messages
      if not log_opt["enabled"]:
        from flask import logging as flask_logging
        from logging import CRITICAL
        flask_logging.getLogger('werkzeug').setLevel(CRITICAL)

    except KeyError:
      self._log.warning("Server settings not found (%s), use default ones", KeyError)

  def start(self):
    mode = "debug" if self._settings["debug"] else "normal"
    self._log.info("Starting server in %s mode on %s:%s", mode, self._settings["host"], self._settings["port"])
    self._flask.run(host=self._settings["host"],
                     port=self._settings["port"],
                     debug=self._settings["debug"]
                    )

  def route(self, rule, **options):
    """
     Stub to pass decorator back to flask, actually doing almost same thing as flask decorator

     Difference is in return value, view can return any value which could pass stringify str() function in debug mode
     and serialization via json for normal mode
    """
    # here is decorator work
    def decorator(f):

      # here we make some trick, and push back only json string, except we are in debug mode
      def wrapper(*args, **kwargs):
        try:
          return json.dumps({
            'query': rule,
            'status': 'OK',
            'data': f(*args, **kwargs)
          })
        except Exception as err:
          import traceback
          return json.dumps({
            'query': rule,
            'status': 'ERROR',
            'data': str(err)
          })

      def debbug_wrapper(*args, **kwargs):
        return str(f(*args, **kwargs))

      endpoint = options.pop('endpoint', None)

      # for debugging we could ignore json transforms and rest notation
      if self._settings["debug"] and self._settings["debug_level"] >= 100:
        debbug_wrapper.__name__ = "%s_wrap" % f.__name__
        self._flask.add_url_rule(rule, endpoint, debbug_wrapper, **options)
      else:  # pack response in-to json response as for rest api
        wrapper.__name__ = "%s_wrap" % f.__name__
        self._flask.add_url_rule(rule, endpoint, wrapper, **options)

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

