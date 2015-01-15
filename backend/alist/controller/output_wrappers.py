import json
from flask import Response


# generate in case if no such wrapper exists
class NoOutputWrapperFound(Exception):
  pass


class AbstractWrapper(object):

  @staticmethod
  def create_response(query: str, status: str, data: str, headers: dict=None, flags: dict=None):
    pass

  @staticmethod
  def response_exception(query: str, exception, headers: dict=None, flags: dict=None):
    pass

  @staticmethod
  def response_http_exception(query: str, http_code: int, exception, flags: dict=None):
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
  def create_response(query: str, status: str, data: str, headers: dict=None, flags: dict=None):
    response = {
      'query': query,
      'status': status,
      'data': data
    }
    if headers is not None:
      response.update(headers)
    return Response(json.dumps(response), mimetype='application/json')

  @staticmethod
  def response_exception(query: str, exception, headers: dict=None, flags: dict=None):
    return JsonWrapper.create_response(query, "ERROR", str(exception), headers, flags=flags)

  @staticmethod
  def response_http_exception(query: str, http_code: int, exception, flags: dict=None):
    return JsonWrapper.response_exception(query, exception, {'http_code': str(http_code)}, flags=flags)

  @staticmethod
  def response_by_function_call(query: str, func, flags: dict=None, *args, **kwargs):
    try:
     return JsonWrapper.create_response(query, "OK", func(*args, **kwargs), flags=flags)
    except Exception as e:
     return JsonWrapper.response_exception(query, e, flags=flags)


class JsonpWrapper(JsonWrapper):
  @staticmethod
  def create_response(query: str, status: str, data: str, headers: dict=None, flags: dict=None):
    callback = "jsonp_func"
    if flags is not None and "callback" in flags and flags["callback"] != "":
      callback = flags["callback"]

    response = JsonWrapper.create_response(query, status, data, headers, flags)
    response.headers['Content-Type'] = "application/javascript"
    response.set_data(
      "%s(%s)" % (callback, response.get_data(as_text=True))
    )
    return response

  @staticmethod
  def response_by_function_call(query: str, func, flags: dict=None, *args, **kwargs):
    try:
      return JsonpWrapper.create_response(query, "OK", func(*args, **kwargs), flags=flags)
    except Exception as e:
      return JsonpWrapper.response_exception(query, e, flags=flags)

class StringWrapper(AbstractWrapper):
  @staticmethod
  def create_response(query: str, status: str, data: str, headers: dict=None, flags: dict=None):
    response = """<b>Query:</b> %s<br/>
                  <b>Status:</b> %s<br/>
                  <b>Data:</b> %s<br/>""" % (query, status, data)

    if headers is not None:
      response += "<b>Headers:</b> %s" % str(headers)
    return Response(response, mimetype='text/html')

  @staticmethod
  def response_exception(query: str, exception, headers: dict=None, flags: dict=None):
    return StringWrapper.create_response(query, "ERROR", str(exception), headers, flags=flags)

  @staticmethod
  def response_http_exception(query: str, http_code: int, exception, flags: dict=None):
    return StringWrapper.response_exception(query, exception, {'http_code': str(http_code)}, flags=flags)

  @staticmethod
  def response_by_function_call(query: str, func, flags: dict=None, *args, **kwargs):
    try:
      return StringWrapper.create_response(query, "OK", func(*args, **kwargs), flags=flags)
    except Exception as e:
      return StringWrapper.response_exception(query, e, flags=flags)