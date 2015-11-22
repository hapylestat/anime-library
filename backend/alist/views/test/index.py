
import alist.controller.main as main
from alist.providers.local.storage_api_provider import StorageApiProvider, ProviderProperties, StorageNotPresentException
from alist.providers.local.disk_provider import DiskProvider

from alist.providers.filters.store_filter import StoreFilter
app = main.Application.get_instance()
store = StorageApiProvider()
local_store = DiskProvider()
myfilter = StoreFilter()


def __init__():
  storage_cfg = app.cfg.get_module_config(app._settings["storage_module"])
  for cfg_item in storage_cfg:
    crypt = 'encrypted' in cfg_item and cfg_item["encrypted"]
    enabled = 'enabled' in cfg_item and cfg_item["enabled"]
    level = None if 'level' not in cfg_item else cfg_item["level"]
    if enabled:
      key = app._settings["storage_api_secret"] if crypt else None
      if not isinstance(cfg_item["type"], list):
        cfg_item["type"] = [cfg_item["type"]]
      try:
        if 'remote' in cfg_item["type"] and 'service' in cfg_item:
          store.add_storage(cfg_item["name"], ProviderProperties(service=cfg_item["service"], secret=key))

        if 'remote' in cfg_item["type"] and 'location' in cfg_item:
          store.add_storage(cfg_item["name"], ProviderProperties(location=cfg_item["location"], secret=key))

        if 'local' in cfg_item["type"] and 'location' in cfg_item:
          local_store.add_storage(cfg_item["name"], ProviderProperties(location=cfg_item["location"], level=level))

      except StorageNotPresentException:
        pass


@app.route("/test")
def view_test(args):
  return myfilter.filter(args["q"])


@app.route("/test/<name>")
def view_test_name(name):
  return "Passed name is: %s" % name


@app.route("/test/store")
def view_store():
  return store.storages + local_store.storages


@app.route("/test/store/<name>")
def view_store_disk(args, name):
  if name in store.storages:
    s = store
  else:
    s = local_store

  if "list" in args:
    return myfilter.filter(s.get_storage(name))
  else:
    return s.get_storage(name)

