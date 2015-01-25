
import alist.controller.main as main
from alist.providers.local.storage_api_provider import StorageApiProvider, ProviderProperties

app = main.Application.get_instance()
store = StorageApiProvider()

def __init__():
  storage_cfg = app.cfg.get_module_config(app._settings["storage_module"])
  for cfg_item in storage_cfg:
    crypt = 'encrypted' in cfg_item and cfg_item["encrypted"]
    key  = app._settings["storage_api_secret"] if crypt else None
    if not isinstance(cfg_item["type"], list):
      cfg_item["type"] = [cfg_item["type"]]

    if 'remote' in cfg_item["type"] and 'service' in cfg_item:
      store.add_storage(cfg_item["name"], ProviderProperties(service=cfg_item["service"], secret=key))

    if 'remote' in cfg_item["type"] and 'location' in cfg_item:
      store.add_storage(cfg_item["name"], ProviderProperties(location=cfg_item["location"], secret=key))



@app.route("/test")
def view_test(args):
  try:
    app.aa += 1
  except:
    app.aa = 1

  return "This is a TEST! %s <br> %s" % (app.aa, args)


@app.route("/test/<name>")
def view_test_name(name):
  return "Passed name is: %s" % name

@app.route("/test/store")
def view_store():
  return store.storages

@app.route("/test/store/<name>")
def view_store_disk(name):
  return store.get_storage(name)

