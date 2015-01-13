from alist.helper.singleton import Singleton, SingletonObject
from alist.logger import alogger
from alist.config import Configuration
from alist.controller.output_wrappers import ResponseWrapperFactory

from flask import Flask


@Singleton
class Application(SingletonObject):
  # set default values
  _settings = {
    "port": 9000,
    "host": "127.0.0.1",
    "debug": False,
    "debug_level": 0,
    "output": "json"
  }

  _flask = None
  # init internal objects
  cfg = None

  def __init__(self):
    self.cfg = Configuration.get_instance()
    self._log = alogger.getLogger(__name__, cfg=self.cfg)
    self._apply_settings()
    self._flask = Flask(__name__)
    self._flask.register_error_handler(404, self._error_404_handler)
    self._flask.register_error_handler(500, self._error_500_handler)

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

      # for debugging we could ignore json transforms and rest notation
      if self._settings["debug"] and self._settings["debug_level"] >= 100:
        self._settings["output"] = "string"

    except KeyError:
      self._log.warning("Server settings not found (%s), use default ones", KeyError)
    except ValueError as err:
      self._log.error("Was passed unknown or wrong parameters. Please check configuration items, shutting down.")

  def start(self):
    mode = "debug" if self._settings["debug"] else "normal"
    self._log.info("Starting server in %s mode on %s:%s", mode, self._settings["host"], self._settings["port"])
    self._flask.run(host=self._settings["host"],
                     port=self._settings["port"],
                     debug=self._settings["debug"]
                    )

  def _error_404_handler(self, e):
    return ResponseWrapperFactory.get_wrapper(self._settings["output"]).response_http_exception("", 404, Exception("Not found")), 404

  def _error_500_handler(self, e):
    return ResponseWrapperFactory.get_wrapper(self._settings["output"]).response_http_exception("", 500, e), 500

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
        return ResponseWrapperFactory.get_wrapper(self._settings["output"]).response_by_function_call(rule, f, *args, **kwargs)

      endpoint = options.pop('endpoint', None)
      wrapper.__name__ = "%s_wrap" % f.__name__
      self._flask.add_url_rule(rule, endpoint, wrapper, **options)

      return f
    return decorator

