from alist.providers.filters.abstract_filter import AbstractFilter


class StoreFilter(AbstractFilter):
  def __init__(self, filters: list):
    super(StoreFilter, self).__init__(filters)
    self._filter_types["dict"] = self._filter_dict


  def _filter_dict(self, item: dict):
      pass

  def _filter_str(self, item: str):
    pass

  def _filter_list(self, item: list):
    pass
