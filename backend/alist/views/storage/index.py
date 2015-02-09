
from alist.controller.main import Application
from alist.providers.local.disk_provider import DiskProvider, ProviderProperties
from alist.helper.token import TokenHelper

app = Application.get_instance()
storage = DiskProvider()
token = TokenHelper(app._settings["storage_api_secret"])
check_token = app._settings["storage_api_check_token"]


def __init__():
  global app, storage

  storage_cfg = app.cfg.get_module_config(app._settings["storage_module"])
  if not isinstance(storage_cfg, list):
    raise Exception("Wrong storage configuration")

  for cfg_item in storage_cfg:
    level = None
    if "level" in cfg_item:
      level = cfg_item["level"]

    if not isinstance(cfg_item["type"], list):
      cfg_item["type"] = [cfg_item["type"]]

    if "local" in cfg_item["type"]:
      storage.add_storage(cfg_item["name"], ProviderProperties(location=cfg_item["location"], level=level))

  rule = app._settings["endpoints"]["storage"]
  if rule == "":
    rule = "/storage"

  app.add_route(rule=rule, f=main, methods=['GET'])


def main(args, headers):
  global check_token
  if check_token:
    key = headers.get('access_key')
    if key is None:
      raise Exception('Access denied, no key found')
    token.parse_token(key)  # check if token is valid

  action = args["q"] if "q" in args else "list"
  store = args["storage"] if "storage" in args else "none"
  if action == "list":
    return storage_list()
  if action == "view":
    return storage_view(store)

  raise Exception("Unknown action")


def storage_view(store: str):
  global storage
  if store not in storage.storages:
    raise Exception("Provided storage name '%s' not found" % store)
  else:
    return storage.get_storage(store)


def storage_list():
  return storage.storages