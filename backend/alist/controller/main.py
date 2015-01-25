from flask import Flask, request

from alist.helper.singleton import Singleton, SingletonObject
from alist.logger import alogger
from alist.config import Configuration
from alist.controller.output_wrappers import ResponseWrapperFactory
import alist.views


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
    self._flask.register_error_handler(405, self._error_405_handler)
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
      self._settings.update({
        "host": self.cfg.get("server.host", check_type=str),
        "port": self.cfg.get("server.port", default=9000, check_type=int),
        "debug": self.cfg.get("server.debug.enabled", default=False, check_type=bool),
        "external_debug": self.cfg.get("server.debug.external_debug", default=False, check_type=bool),
        "debug_level": self.cfg.get("server.debug.debug_level", default=0, check_type=int),
        "enable_jsonp": self.cfg.get("server.api.enable_jsonp", default=False, check_type=bool),
        "api_enabled": self.cfg.get("server.api.enabled", default=True, check_type=bool),
        "static_enabled": self.cfg.get("server.static.enabled", default=False, check_type=bool),
        "static_path": self.cfg.get("server.static.path", default="", check_type=str),
        "static_index": self.cfg.get("server.static.index", default="", check_type=str),
        "storage_api_enabled": self.cfg.get("server.storage-api.enabled", default=False, check_type=bool),
        "storage_api_secret": self.cfg.get("server.storage-api.secret", default="", check_type=str),
        "storage_module": self.cfg.get("server.storage-api.storage-module", default="storage", check_type=str),
        "storage_api_check_token": self.cfg.get("server.storage-api.check_token", default=True, check_type=bool),
        "endpoints": {
          "api": self.cfg.get("server.api.endpoint", default="/api", check_type=str),
          "static": self.cfg.get("server.static.endpoint", default="/", check_type=str),
          "storage": self.cfg.get("server.storage-api.endpoint", default="/storage", check_type=str)
        }
      })
      # ToDo: Check endpoints to be not math one location

      if self._settings["endpoints"]["api"][-1:] == "/":
        self._settings["endpoints"]["api"] = self._settings["endpoints"]["api"][:-1]
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

    self._load_views()

    #start server
    self._flask.run(**flask_args)

  def _load_views(self):
    exclude_list = []
    include_list = []
    if not self._settings["storage_api_enabled"]:
      exclude_list.append("storage.index")
    else:
      include_list.append("storage.index")

    if self._settings["api_enabled"]:
      alist.views.load(disabled_views=exclude_list)
    elif len(include_list) > 0:
      alist.views.load(allowed_views=include_list)

  def _error_404_handler(self, e):
    return self._response_wrapper.response_http_exception("", 404, Exception("Not found")), 404

  def _error_500_handler(self, e):
    return self._response_wrapper.response_http_exception("", 500, e), 500

  def _error_405_handler(self, e):
    return self._response_wrapper.response_http_exception("", 405, e), 405

  def route(self, rule, **options):
    """
     Stub to pass decorator back to flask, actually doing almost same thing as flask decorator

     Difference is in return value, view can return any value which could pass stringify str() function in debug mode
     and serialization via json for normal mode
    """
    # here is decorator work
    def decorator(f):
      self.add_route(rule, f, **options)

    return decorator

  def add_route(self, rule, f, **options):
    # here we make some trick, and push back only json string, except we are in debug mode
    def wrapper(*args, **kwargs):
      req_args = request.args.to_dict()
      if 'args' in f.__code__.co_varnames:
        kwargs["args"] = req_args
      if 'headers_dict' in f.__code__.co_varnames:
        headers = {}
        for item in request.headers:
          headers.update({item[0]: item[1]})
        kwargs["headers_dict"] = headers
      if 'headers' in f.__code__.co_varnames:
        kwargs["headers"] = request.headers

      if self._settings["enable_jsonp"] and 'jsonp' in req_args:
        return ResponseWrapperFactory.get_wrapper("jsonp").response_by_function_call(request.path, f, flags={'callback': req_args["jsonp"]}, *args, **kwargs)

      return self._response_wrapper.response_by_function_call(request.path, f, *args, **kwargs)

    endpoint = options.pop('endpoint', None)
    wrapper.__name__ = "%s_wrap" % f.__name__
    self._flask.add_url_rule("%s%s" % (self._settings["endpoints"]["api"], rule), endpoint, wrapper, **options)

    return f

  def serve_static_content(self):
    def static_route(path):
      return self._flask.send_static_file(path)

    def static_index():
      return self._flask.send_static_file(self._settings["static_index"])

    route = "%s/<path:path>" % (self._settings["endpoints"]["static"] if self._settings["endpoints"]["static"] != "/" else "")

    self._flask.add_url_rule(self._settings["endpoints"]["static"], view_func=static_index)
    self._flask.add_url_rule(route, view_func=static_route)

