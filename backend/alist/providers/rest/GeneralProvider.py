
from alist.helper.curl import CURLAuth


"""
 features: is the following dict:
   list - api support list of all anime items
   search - api support search anime by pattern
   get_item - api support of getting detailed info per item
"""


class ApiProviderFeaturesConst(object):
  _feat = [
    "list", "search", "get_item"
  ]

  @property
  def features(self):
    return self._feat

  def __getattr__(self, item):
    if item in self._feat:
      return item
    else:
      raise AttributeError("Unknown attribute: %s" % item)


class ApiProviderFeatures(object):
  def __init__(self, features: list=None):
    if features is not None:
      for feat in features:
        if feat not in ApiProviderFeaturesConst._feat:
          raise AttributeError("Unknown feature item: %s" % feat)
    self._features = features

  @property
  def features(self):
    return self._features

  @property
  def list(self):
    return ApiProviderFeaturesConst.list in self._features

  @property
  def search(self):
    return ApiProviderFeaturesConst.search in self._features

  @property
  def get_item(self):
    return ApiProviderFeaturesConst.get_item in self._features


class GeneralApiProvider(object):
  def __init__(self, auth: CURLAuth=None, features: ApiProviderFeatures=None):
    self._auth = auth
    self._features = features

  @property
  def auth(self):
    raise ValueError("This value could be only to be set")

  @auth.setter
  def auth(self, value: CURLAuth):
    self._auth = value

  @property
  def list(self):
    if self._features.list is False:
      return None
