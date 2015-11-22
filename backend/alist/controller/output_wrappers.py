import json
from datetime import datetime
import traceback

from flask import Response


PRINT_TRACKEROUTE = True
# generate in case if no such wrapper exists
class NoOutputWrapperFound(Exception):
  pass


class AbstractWrapper(object):

  @staticmethod
  def create_response(query: str, status: str, data: str, json_headers: dict=None, headers: dict=None, flags: dict=None):
    pass

  @staticmethod
  def response_exception(query: str, exception, json_headers: dict=None, headers: dict=None, flags: dict=None):
    pass

  @staticmethod
  def response_http_exception(query: str, http_code: int, exception, headers: dict=None, flags: dict=None):
    pass

  @staticmethod
  def response_by_function_call(query: str, func, flags: dict=None, *args, **kwargs):
    pass


class ResponseWrapperFactory(object):
  @staticmethod
  def get_wrapper(wrapper_type: str) -> AbstractWrapper:
    if wrapper_type == "json":
      return JsonWrapper
    if wrapper_type == "jsonp":
      return JsonpWrapper
    if wrapper_type == "string":
      return StringWrapper

    raise NoOutputWrapperFound()


class JsonWrapper(AbstractWrapper):
  @staticmethod
  def create_response(query: str, status: str, data: str, json_headers: dict=None, headers: dict=None, flags: dict=None):
    response = {
      'query': query,
      'status': status,
      'data': data
    }
    if json_headers is not None:
      response.update(json_headers)

    _headers = {
      "Cache-Control": "no-cache, no-store, must-revalidate",
      "Pragma": "no-cache",
      "Expires": "0",
    }

    if headers is not None:
      _headers.update(headers)

    return Response(json.dumps(response), mimetype='application/json', headers=_headers)

  @staticmethod
  def response_exception(query: str, exception, json_headers: dict=None, headers: dict=None, flags: dict=None):
    error_msg = "Type: %s, Data: %s" % (type(exception).__name__, str(exception))
    return JsonWrapper.create_response(query, "ERROR", error_msg, json_headers, headers=headers, flags=flags)

  @staticmethod
  def response_http_exception(query: str, http_code: int, exception, headers: dict=None, flags: dict=None):
    return JsonWrapper.response_exception(query, exception, {'http_code': str(http_code)}, headers=headers, flags=flags)

  @staticmethod
  def response_by_function_call(query: str, func, flags: dict=None, *args, **kwargs):
    try:
      b_time = datetime.now()
      headers = {}
      data = func(*args, **kwargs)
      if isinstance(data, tuple):
        headers.update(data[0])
        data = data[1]
      json_headers = {
        "execution": str(datetime.now() - b_time)
      }
      return JsonWrapper.create_response(query, "OK", data, json_headers=json_headers, headers=headers, flags=flags)
    except Exception as e:
      tb = ""
      if PRINT_TRACKEROUTE:
        tb = traceback.format_exc().splitlines()
      return JsonWrapper.response_exception(query, e, json_headers={'out': tb}, flags=flags)


class JsonpWrapper(JsonWrapper):
  @staticmethod
  def create_response(query: str, status: str, data: str, json_headers: dict=None, headers: dict=None, flags: dict=None):
    callback = "jsonp_func"
    if flags is not None and "callback" in flags and flags["callback"] != "":
      callback = flags["callback"]

    response = JsonWrapper.create_response(query, status, data, json_headers, headers=headers, flags=flags)
    response.headers['Content-Type'] = "application/javascript"
    response.set_data(
      "%s(%s)" % (callback, response.get_data(as_text=True))
    )
    return response

  @staticmethod
  def response_by_function_call(query: str, func, flags: dict=None, *args, **kwargs):
    try:
      b_time = datetime.now()
      data = func(*args, **kwargs)
      headers = {}
      if isinstance(data, tuple):
        headers.update(data[0])
        data = data[1]
      json_headers = {
        "execution": str(datetime.now() - b_time)
      }
      return JsonpWrapper.create_response(query, "OK", data, json_headers=json_headers, headers=headers, flags=flags)
    except Exception as e:
      tb = ""
      if PRINT_TRACKEROUTE:
        tb = traceback.format_exc().splitlines()
      return JsonpWrapper.response_exception(query, e, json_headers={'out': tb}, flags=flags)


class StringWrapper(AbstractWrapper):
  @staticmethod
  def create_response(query: str, status: str, data: str, json_headers: dict=None, headers: dict=None, flags: dict=None):
    response = """<b>Query:</b> %s<br/>
                  <b>Status:</b> %s<br/>
                  <b>Data:</b> %s<br/>""" % (query, status, data)

    _headers = {
      "Cache-Control": "no-cache, no-store, must-revalidate",
      "Pragma": "no-cache",
      "Expires": "0",
    }

    if headers is not None:
      _headers.update(headers)

    if json_headers is not None:
      response += "<b>json_headers:</b> %s" % str(json_headers)
    return Response(response, mimetype='text/html', headers=_headers)

  @staticmethod
  def response_exception(query: str, exception, json_headers: dict=None, headers: dict=None, flags: dict=None):
    return StringWrapper.create_response(query, "ERROR", str(exception), json_headers, headers=headers, flags=flags)

  @staticmethod
  def response_http_exception(query: str, http_code: int, exception, headers: dict=None, flags: dict=None):
    return StringWrapper.response_exception(query, exception, {'http_code': str(http_code)}, headers=headers, flags=flags)

  @staticmethod
  def response_by_function_call(query: str, func, flags: dict=None, *args, **kwargs):
    try:
      b_time = datetime.now()
      headers = {}
      data = func(*args, **kwargs)
      if isinstance(data, tuple):
        headers = data[0]
        data = data[1]
      json_headers = {
        "execution": str(datetime.now() - b_time)
      }
      return StringWrapper.create_response(query, "OK", data, json_headers=json_headers, headers=headers, flags=flags)
    except Exception as e:
      # ToDo: Rewrite such part of code, more generalize this part
      tb = ""
      if PRINT_TRACKEROUTE:
        tb = traceback.format_exc().splitlines()
      return StringWrapper.response_exception(query, e, json_headers={'out': tb}, flags=flags)