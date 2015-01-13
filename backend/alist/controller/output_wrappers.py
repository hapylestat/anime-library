import json


# generate in case if no such wrapper exists
class NoOutputWrapperFound(Exception):
  pass


class AbstractWrapper(object):

  @staticmethod
  def create_response(query: str, status: str, data: str, headers: dict=None):
    pass

  @staticmethod
  def response_exception(query: str, exception, headers: dict=None):
    pass

  @staticmethod
  def response_http_exception(query: str, http_code: int, exception):
    pass

  @staticmethod
  def response_by_function_call(query: str, func, *args, **kwargs):
    pass


class ResponseWrapperFactory(object):
  @staticmethod
  def get_wrapper(wrapper_type: str) -> AbstractWrapper:
    if wrapper_type == "json":
      return JsonWrapper
    if wrapper_type == "string":
      return StringWrapper

    raise NoOutputWrapperFound()


class JsonWrapper(AbstractWrapper):
  @staticmethod
  def create_response(query: str, status: str, data: str, headers: dict=None):
    response = {
      'query': query,
      'status': status,
      'data': data
    }
    if headers is not None:
      response.update(headers)
    return json.dumps(response)

  @staticmethod
  def response_exception(query: str, exception, headers: dict=None):
    return JsonWrapper.create_response(query, "ERROR", str(exception), headers)

  @staticmethod
  def response_http_exception(query: str, http_code: int, exception):
    return JsonWrapper.response_exception(query, exception, {'http_code': str(http_code)})

  @staticmethod
  def response_by_function_call(query: str, func, *args, **kwargs):
    try:
     return JsonWrapper.create_response(query, "OK", func(*args, **kwargs))
    except Exception as e:
     return JsonWrapper.response_exception(query, e)


class StringWrapper(AbstractWrapper):
  @staticmethod
  def create_response(query: str, status: str, data: str, headers: dict=None):
    response = """<b>Query:</b> %s<br/>
                  <b>Status:</b> %s<br/>
                  <b>Data:</b> %s<br/>""" % (query, status, data)

    if headers is not None:
      response += "<b>Headers:</b> %s" % str(headers)
    return response

  @staticmethod
  def response_exception(query: str, exception, headers: dict=None):
    return StringWrapper.create_response(query, "ERROR", str(exception), headers)

  @staticmethod
  def response_http_exception(query: str, http_code: int, exception):
    return StringWrapper.response_exception(query, exception, {'http_code': str(http_code)})

  @staticmethod
  def response_by_function_call(query: str, func, *args, **kwargs):
    try:
      return StringWrapper.create_response(query, "OK", func(*args, **kwargs))
    except Exception as e:
      return StringWrapper.response_exception(query, e)