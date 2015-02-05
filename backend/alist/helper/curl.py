
import sys
if sys.version_info.major == 3:
  from urllib.request import HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler, Request, build_opener
  from urllib.parse import urlencode
else:
  from urllib2 import HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler, Request, build_opener
  from urllib import urlencode


class CURLResponse(object):
  def __init__(self, director_open_result):
    self._code = director_open_result.code
    self._headers = director_open_result.info()
    self._content = director_open_result.read()

  @property
  def code(self):
    return self._code

  @property
  def headers(self):
    return self._headers

  @property
  def content(self):
    return self._content


class CURLAuth(object):
  def __init__(self, user, password):
    self._user = user
    self._password = password

  @property
  def user(self):
    return self._user

  @property
  def password(self):
    return self._password


def curl(url: str, params: dict=None, auth: CURLAuth=None,
         req_type: ['GET', 'PUT', 'POST', 'DELETE']='GET',
         data=None, headers: dict=None) -> CURLResponse:
  """
  Make request to web resource
  :param url: Url to endpoint
  :param params: list of params after "?"
  :param auth: authorization tokens
  :param req_type: type of the request
  :param data: data which need to be posted
  :param headers: headers which would be posted with request
  :return: Response object
  """
  post_req = ["POST", "PUT"]
  get_req = ["GET", "DELETE"]

  if params is not None:
    url += "?" + urlencode(params)

  if req_type not in post_req + get_req:
    raise IOError("Wrong request type \"%s\" passed" % req_type)

  _headers = {}
  handler_chain = []

  if auth is not None:
    manager = HTTPPasswordMgrWithDefaultRealm()
    manager.add_password(None, url, auth.user, auth.password)
    handler_chain.append(HTTPBasicAuthHandler(manager))

  if req_type in post_req and data is not None:
    _headers["Content-Length"] = len(data)

  if headers is not None:
    _headers.update(headers)

  director = build_opener(*handler_chain)

  if req_type in post_req:
    if sys.version_info.major == 3:
      _data = bytes(data, encoding='utf8')
    else:
      _data = bytes(data)

    req = Request(url, headers=_headers, data=_data)
  else:
    req = Request(url, headers=_headers)

  req.get_method = lambda: req_type

  return CURLResponse(
    director.open(req)
  )
