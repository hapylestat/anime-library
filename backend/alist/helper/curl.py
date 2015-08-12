# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# Copyright (c) 2015 Reishin <hapy.lestat@gmail.com>


import sys
import json
import base64
import gzip
import zlib

if sys.version_info.major == 3:
  from urllib.request import HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler, Request, build_opener, URLError, HTTPError
  from urllib.parse import urlencode
  from io import BytesIO
else:
  from urllib2 import HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler, Request, build_opener, URLError, HTTPError
  from urllib import urlencode
  from StringIO import StringIO as BytesIO


class CURLResponse(object):
  def __init__(self, director_open_result):
    self._code = director_open_result.code
    self._headers = director_open_result.info()
    self._content = director_open_result.read()

  def __decode_response(self, data):
    data = self.__decode_compressed(data)
    if isinstance(data, bytes) and "Content-Type" in self._headers and "charset" in self._headers["Content-Type"]:
      charset = list(filter(lambda x: "charset" in x, self._headers["Content-Type"].split(';')))
      if len(charset) > 0:
        charset = charset[0].split('=')
        if len(charset) == 2:
          return data.decode(charset[1].lower())
      return data.decode('utf-8')
    elif isinstance(data, bytes):
      return data.decode('utf-8')
    else:
      return data

  def __decode_compressed(self, data):
    if isinstance(data, bytes) and "Content-Encoding" in self._headers:

      if "gzip" in self._headers["Content-Encoding"] or 'x-gzip' in self._headers["Content-Encoding"]:
        data = gzip.GzipFile(fileobj=BytesIO(data)).read()
      elif "deflate" in self._headers["Content-Encoding"]:
        data = zlib.decompress(data)

    return data

  @property
  def code(self):
    return self._code

  @property
  def headers(self):
    return self._headers

  @property
  def content(self):
    return self.__decode_response(self._content)

  @property
  def raw(self):
    return self._content

  def from_json(self):
    try:
      return json.loads(self.content)
    except ValueError:
      return None


class CURLAuth(object):
  def __init__(self, user, password, force=False, headers: dict=None):
    self._user = user
    self._password = password
    self._force = force  # Required if remote doesn't support http 401 response
    self._headers = headers

  @property
  def user(self):
    return self._user

  @property
  def password(self):
    return self._password

  @property
  def force(self):
    return self._force

  @property
  def headers(self):
    if not self._force:
      return self._headers
    else:
      ret_temp = {}
      ret_temp.update(self._headers)
      ret_temp.update(self.get_auth_header())
      return ret_temp

  def get_auth_header(self):
    token = "%s:%s" % (self.user, self.password)
    if sys.version_info.major == 3:
      token = base64.encodebytes(bytes(token, encoding='utf8')).decode("utf-8")
    else:
      token = base64.encodestring(token)

    return {
      "Authorization": "Basic %s" % token.replace('\n', '')
    }


def curl(url: str, params: dict=None, auth: CURLAuth=None,
         req_type: str='GET',
         data=None, headers: dict=None, timeout: int=None, use_gzip: bool=True) -> CURLResponse:
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

  # apply encoding to content
  if req_type in post_req and data is not None:
    if sys.version_info.major == 3:
      _data = bytes(data, encoding='utf8')
    else:
      _data = bytes(data)

  # process gzip
  if use_gzip:
    if "Accept-Encoding" in _headers:
      if "gzip" not in _headers["Accept-Encoding"]:
        _headers["Accept-Encoding"] += ", gzip, x-gzip, deflate"
    else:
      _headers["Accept-Encoding"] = "gzip, x-gzip, deflate"

  if auth is not None and auth.force is False:
    manager = HTTPPasswordMgrWithDefaultRealm()
    manager.add_password(None, url, auth.user, auth.password)
    handler_chain.append(HTTPBasicAuthHandler(manager))

  if auth is not None and auth.force:
    _headers.update(auth.headers)

  if req_type in post_req and data is not None:
    _headers["Content-Length"] = len(data)

  if headers is not None:
    _headers.update(headers)

  director = build_opener(*handler_chain)

  if req_type in post_req:
    req = Request(url, headers=_headers, data=_data)
  else:
    req = Request(url, headers=_headers)

  req.get_method = lambda: req_type

  try:
    if timeout is not None:
      return CURLResponse(director.open(req, timeout=timeout))
    else:
      return CURLResponse(director.open(req))
  except URLError as e:
    if isinstance(e, HTTPError):
      raise e
    else:
      raise TimeoutError
