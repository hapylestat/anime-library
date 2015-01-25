
from alist.controller.main import Application
from alist.providers.local.disk_provider import DiskProvider, ProviderProperties
from alist.helper.token import TokenHelper

app = Application.get_instance()
storage = DiskProvider()
token = TokenHelper(app._settings["storage_api_secret"])


def __init__():
  global app, storage

  storage_cfg = app.cfg.get_module_config(app._settings["storage_module"])
  if not isinstance(storage_cfg, list):
    raise Exception("Wrong storage configuration")

  for cfg_item in storage_cfg:
    if not isinstance(cfg_item["type"], list):
      cfg_item["type"] = [cfg_item["type"]]

    if "local" in cfg_item["type"]:
      storage.add_storage(cfg_item["name"], ProviderProperties(location=cfg_item["location"]))

  rule = app._settings["endpoints"]["storage"]
  if rule == "":
    rule = "/storage"

  app.add_route(rule=rule, f=main)


def main(args):
  action = args["q"] if "q" in args else "list"
  store = args["storage"] if "storage" in args else "none"

  if action == "list":
    return storage_list()
  if action == "view":
    return storage_view(store)
  if action == "test":
    t = token.make_token({"fs": "fds"})
    return {
      "make": t,
      "decode": token.parse_token(t)
    }


def storage_view(store: str):
  global storage
  if store not in storage.storages:
    raise Exception("Provided storage name '%s' not found" % store)
  else:
    return storage.get_storage(store)


def storage_list():
  return storage.storages