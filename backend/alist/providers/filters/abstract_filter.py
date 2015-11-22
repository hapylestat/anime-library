
import re
"""
Filter dict example:
{
 "<regexp>": {
   "replace": "<replace math>",
   "level": <level of filter, from 0 to 100, default 0>,
   "order": <apply order of the filter>
 }
}
"""


class AbstractFilter(object):
  _c_compiled_filter = "regex_c"
  _c_filter = "regex"
  _c_replace = "replace"
  _c_level = "level"
  _c_order = "order"
  _c_case = "ignore-case"

  def __init__(self, filters: list):
    self._filter_types = {
      "str": self._base_string_filter
    }

    if filters is None:
      raise ValueError("Filters args can't be none")

    # "magic" filter
    self._magic_filter = re.compile("\{([^\{\}]+)\}")

    self._parse_filter(filters)

  def _parse_filter(self, filters: list):
    def _chk_item(item: dict):
      if self._c_level not in item:
        item.update({self._c_level: 0})
      if self._c_order not in item:
        item.update({self._c_order: 0})
      if self._c_replace not in item:
        item.update({self._c_replace: ""})
      if self._c_case not in item:
        item.update({self._c_case: False})

      # compile pattern with ignore-case flag
      if item[self._c_case]:
        item.update({
          self._c_compiled_filter: re.compile(item[self._c_filter], re.IGNORECASE)
        })
      else:
        item.update({
         self._c_compiled_filter: re.compile(item[self._c_filter])
        })

      return item
    # step 1. Add missing keys with defaults, pre-compile regexp
    filters = map(lambda x: _chk_item(x), filters)

    # step 2. sort by level
    self._filters = sorted(filters, key=lambda x: x[self._c_order])

  def filter(self, item):
    item_type = type(item).__name__
    if item_type in self._filter_types:
      return self._filter_types[item_type](item)
    else:
      raise ValueError("Can't filter type %s, support only: %s" % (item_type, ",".join(self._filter_types.keys())))

  def _base_string_filter(self, item: str):
    math_magic = re.search(self._magic_filter, item)
    if math_magic:
      g = math_magic.groups()
      if len(g) > 0:
        return g[0]
    else:
      for f in self._filters:
        item = re.sub(f[self._c_compiled_filter], f[self._c_replace], item)
    return item.strip()