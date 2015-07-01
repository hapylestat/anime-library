from alist.providers.filters.abstract_filter import AbstractFilter
from alist.config import Configuration


class StoreFilter(AbstractFilter):
  def __init__(self):
    filters = Configuration.get_instance().get_module_config("storage_filter")
    if filters is None:
      raise ValueError("Storage filter is not present")

    super(StoreFilter, self).__init__(filters)
    self._filter_types["dict"] = self._filter_dict
    self._filter_types["list"] = self._filter_list

  def _filter_dict(self, item: dict):
    def filter_sub_key(target_dict: dict):
      keys = list(target_dict.keys())
      while len(keys) > 0:
        key = keys.pop(0)
        if isinstance(target_dict[key], dict):
          target_dict[key] = filter_sub_key(target_dict[key])
        target_dict[self._base_string_filter(key)] = target_dict.pop(key)
      return target_dict

    return filter_sub_key(item)

  def _filter_list(self, item: list):
    return list(map(lambda x: self._base_string_filter(x), item))
