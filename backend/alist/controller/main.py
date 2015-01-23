from alist.helper.singleton import Singleton, SingletonObject
from alist.logger import alogger
from alist.config import Configuration
from alist.controller.output_wrappers import ResponseWrapperFactory

from os import environ
from flask import Flask, request


@Singleton
class Application(SingletonObject):
  # set default values
  _settings = {
    "port": 9000,
    "host": "127.0.0.1",
    "debug": False,
    "external_debug": False,
    "debug_level": 0,
    "output": "json",
    "enable_jsonp": False
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
    self._response_wrapper = ResponseWrapperFactory.get_wrapper(self._settings["output"])

    # serve static content, please use that possibility only for testing.
    # in production please use nginx, apache, etc for this.
    if self._settings["static_enabled"]:
      self._log.info("Static content serving enabled, serving \"%s\" at mountpoint \"%s\"" %
                     (self._settings["static_path"], self._settings["static_endpoint"]))
      self._flask.static_folder = self._settings["static_path"]
      self.serve_static_content()

  def _apply_settings(self):
    try:
      self._settings["host"] = self.cfg.get("server.host", check_type=str)
      self._settings["port"] = self.cfg.get("server.port", default=9000, check_type=int)
      self._settings["debug"] = self.cfg.get("server.debug.enabled", default=False, check_type=bool)
      self._settings["external_debug"] = self.cfg.get("server.debug.external_debug", default=False, check_type=bool)
      self._settings["debug_level"] = self.cfg.get("server.debug.debug_level", default=0, check_type=int)
      self._settings["enable_jsonp"] = self.cfg.get("server.api.enable_jsonp", default=False, check_type=bool)
      self._settings["api_endpoint"] = self.cfg.get("server.api.endpoint", default="", check_type=str)
      self._settings["static_endpoint"] = self.cfg.get("server.static.endpoint", default="", check_type=str)
      self._settings["static_enabled"] = self.cfg.get("server.static.enabled", default=False, check_type=bool)
      self._settings["static_path"] = self.cfg.get("server.static.path", default="", check_type=str)
      self._settings["static_index"] = self.cfg.get("server.static.index", default="", check_type=str)

      if self._settings["api_endpoint"][-1:] == "/":
        self._settings["api_endpoint"] = self._settings["api_endpoint"][:-1]
      # set highest log level for flask to suppress info messages
      if not self.cfg.get("logging.enabled", default=False, check_type=bool):
        from flask import logging as flask_logging
        alogger.setLogLevel(flask_logging.getLogger('werkzeug'), "critiacal")
      else:
        from flask import logging as flask_logging
        not self.cfg.get("logging.url_log", default=True, check_type=bool) and alogger.setLogLevel(flask_logging.getLogger('werkzeug'), "ERROR")


      # for debugging we could ignore json transforms and rest notation
      if self._settings["debug"] and self._settings["debug_level"] >= 100:
        self._settings["output"] = "string"

      if self._settings["output"] != "json":  # disable jsonp if base filter is not json
        self._settings["enable_jsonp"] = False
    except KeyError:
      self._log.warning("Server settings not found (%s), use default ones", KeyError)
    except ValueError as err:
      self._log.error("Was passed unknown or wrong parameters. Please check configuration items, shutting down.")

  def start(self):
    mode = "debug" if self._settings["debug"] else "normal"
    self._log.info("Starting server in %s mode on %s:%s", mode, self._settings["host"], self._settings["port"])
    flask_args = {
      "threaded": True,
      "host": self._settings["host"],
      "port": self._settings["port"],
      "debug": self._settings["debug"]
    }
    if self._settings["external_debug"] and self._settings["debug"]:
      flask_args["use_debugger"] = False
      flask_args["use_reloader"] = False

    self._flask.run(**flask_args)

  def _error_404_handler(self, e):
    return self._response_wrapper.response_http_exception("", 404, Exception("Not found")), 404

  def _error_500_handler(self, e):
    return self._response_wrapper.response_http_exception("", 500, e), 500

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
        req_args = request.args.to_dict()
        if 'args' in f.__code__.co_varnames:
          kwargs["args"] = req_args

        if self._settings["enable_jsonp"] and 'jsonp' in req_args:
          return ResponseWrapperFactory.get_wrapper("jsonp").response_by_function_call(request.path, f, flags={'callback': req_args["jsonp"]}, *args, **kwargs)

        return self._response_wrapper.response_by_function_call(request.path, f, *args, **kwargs)

      endpoint = options.pop('endpoint', None)
      wrapper.__name__ = "%s_wrap" % f.__name__
      self._flask.add_url_rule("%s%s" % (self._settings["api_endpoint"], rule), endpoint, wrapper, **options)

      return f
    return decorator

  def serve_static_content(self):
    def static_route(path):
      return self._flask.send_static_file(path)

    def static_index():
      return self._flask.send_static_file(self._settings["static_index"])

    route = "%s/<path:path>" % (self._settings["static_endpoint"] if self._settings["static_endpoint"] != "/" else "")

    self._flask.add_url_rule(self._settings["static_endpoint"], view_func=static_index)
    self._flask.add_url_rule(route, view_func=static_route)

