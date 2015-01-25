import os

from alist.providers.local.abstract_provider import AbstractProvider, ProviderProperties


class DiskProvider(AbstractProvider):

  def __init__(self, auto_update=True, time: str="0:0:30"):
    super(DiskProvider, self).__init__(auto_update, time)

  def _get_folder(self, data, loc_root):
    t_data = data
    root_el = "/"
    loc_root = loc_root.split("/")  # split path to separate elements
    loc_root[0] = root_el
    last = loc_root.pop()  # extract last element as they could not exists
    if len(t_data) > 0:
      for item in loc_root:
        t_data = t_data[item]

    if last == "":
      last = root_el
    t_data[last] = {}
    return t_data[last]

  def _add_storage(self, name: str, storage: dict, properties: ProviderProperties):
    pass

  def _update_storage(self, name: str, storage: dict, properties: ProviderProperties):
    data = {}

    for root, folders, files in os.walk(properties.location):
     loc_root = root.replace(properties.location, '/').replace(os.sep, '/')
     if properties.level is not None and loc_root.count('/') > properties.level:
       continue

     folder = self._get_folder(data, loc_root)
     folder.update(self._make_folder_item(path=root, files=files))

    return data

  def _get_storage(self, name: str, storage: dict, properties: ProviderProperties):
    return storage["data"]
