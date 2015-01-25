import json

from alist.providers.local.abstract_provider import AbstractProvider, ProviderProperties
from alist.logger import alogger
from alist.config import Configuration
from alist.helper.curl import curl
from alist.helper.token import TokenHelper


class StorageApiProvider(AbstractProvider):
  def __init__(self, auto_update=True, time: str="0:0:30"):
    self._log = alogger.getLogger(__name__, Configuration.get_instance())
    self._storage_list_url = "{0}?q=list"
    self._storage_view_url = "{0}?q=view&storage={1}"
    super(StorageApiProvider, self).__init__(auto_update, time)

  def _service_call(self, url, secret: str=None):
    headers = {}
    if secret is not None:
      headers.update({
        'access_key': TokenHelper(secret).make_token({}, False)
      })

    resp = curl(url, req_type="GET", headers=headers)
    if resp.code != 200:  # check for response code
      self._log.debug("Call to %s failed. Code: %s, Content: %s" % (url, resp.code, resp.content))
      raise Exception("Remote service call failed")

    try:
      json_response = json.loads(resp.content.decode("utf-8"))  # Try to transform response to json
    except ValueError:
      self._log.debug("Call to %s failed. Content: %s" % (url, resp.content))
      raise Exception("Remote service call failed")

    if 'status' in json_response and json_response['status'] == "ERROR":
      self._log.debug("Call to %s failed. Data: %s" % (url, json_response["data"]))
      raise Exception(json_response["data"])

    return json_response["data"]

  def add_storage(self, name: str, properties: ProviderProperties=None):
    if properties.service is None:  # service added using location setting
      super(StorageApiProvider, self).add_storage(name, properties)
    else:
      storage_list = self._service_call(self._storage_list_url.format(properties.service), properties.secret)
      if isinstance(storage_list, list):
        for item in storage_list:
          self.add_storage(item,
                           ProviderProperties(
                             self._storage_view_url.format(properties.service, item),
                             secret=properties.secret,
                             add_trailing_slash=False
                           ))
      else:
        raise Exception("Remote storage exception. List failed")

  def _add_storage(self, name: str, storage: dict, properties: ProviderProperties):
    pass

  def _update_storage(self, name: str, storage: dict, properties: ProviderProperties):
    return self._service_call(properties.location, properties.secret)

  def _get_storage(self, name: str, storage: dict, properties: ProviderProperties):
    return storage["data"]