from datetime import datetime, timedelta
import os

from alist.config import Configuration


class StorageAlreadyPresentException(Exception):
  pass


class StorageNotPresentException(Exception):
  pass


class NoLocationProvidedException(Exception):
  pass


class ProviderProperties(object):
  def __init__(self, location=None, level=None, service=None, secret=None, add_trailing_slash=True):
    if location is not None and add_trailing_slash:
      if location[-len(os.sep):] != os.sep:
        self._location = str(location + os.sep)
      else:
        self._location = str(location)
    else:
      self._location = str(location) if location is not None else location

    self._level = int(level) if level is not None else level
    self._service = str(service) if service is not None else service
    self._secret = str(secret) if secret is not None else secret

  @property
  def location(self):
    return self._location

  @property
  def level(self):
    return self._level

  @property
  def service(self):
    return self._service

  @property
  def secret(self):
    return self._secret


class AbstractProvider(object):
  """
   Abstract storage provider.
   Such services provided as:
    - add storage (just add storage, no update performed)
    - del storage
    - get storage
    - update storage

    Additionally auto-update feature provided for simple systems. If auto_update and time delta is set, during the
    storage_get request storage will be updated automatically. If auto_update is not set, please use update function
     manually, or use external task planner to call update function.
  """
  def __init__(self, auto_update=True, time: str="0:0:30"):
    self.cfg = Configuration.get_instance()
    self._storages = {}
    self._auto_update = auto_update
    self._update_period = self._parsetime(time)

  def _parsetime(self, time: str):
    t_time = ["0", "0", "0.0"]
    time = time.split(":")
    if len(time) == 1:
      t_time[2] = time[0]
    elif len(time) == 2:
      t_time[1] = time[0]
      t_time[2] = time[1]
    elif len(time) == 3:
      t_time = time

    sec_temp = t_time[2].split(".")
    msec = "0"
    if len(sec_temp) == 2:
      msec = sec_temp[1]
    t_time[2] = sec_temp[0]

    return timedelta(hours=int(t_time[0]), minutes=int(t_time[1]), seconds=int(t_time[2]), microseconds=int(msec))

  def add_storage(self, name: str, properties: ProviderProperties=None):
    if name not in self._storages:
      if properties.location is None:
        raise NoLocationProvidedException("No location provided for storage %s" % name)
      self._storages[name] = {
        "properties": properties,
        "last_update": None,
        "data": None
      }
      self._add_storage(name, self._storages[name], properties)
    else:
      raise StorageAlreadyPresentException("Storage %s already present" % name)

  def remove_storage(self, name: str):
    if name in self._storages:
      del self._storages[name]
    else:
      raise StorageNotPresentException("Storage %s not present" % name)

  def update_storage(self, name: str=None):
    if name is None:
      for store in self._storages:
        self._update_storage(store, self._storages[store], self._storages[store]["properties"])
        if self._auto_update:
          self._storages[store]["data"] = self._storages[store]["last_update"] = datetime.now()
    else:
      if name in self._storages:
        self._storages[name]["data"] = self._update_storage(name, self._storages[name], self._storages[name]["properties"])
        if self._auto_update:
          self._storages[name]["last_update"] = datetime.now()

  @property
  def storages(self):
    return list(self._storages.keys())

  def get_storage(self, name: str, call_update=False):
    if name in self._storages:
      if self._auto_update and self._storages[name]["last_update"] is None:  # trigger first update
        self.update_storage(name)
      elif self._auto_update and (datetime.now() - self._storages[name]["last_update"]) > self._update_period:
        self.update_storage(name)

      # trigger update if it's first update, needed in case if auto update disabled
      if self._storages[name]["data"] is None or call_update:
        self.update_storage(name)

      return self._get_storage(name, self._storages[name], self._storages[name]["properties"])
    else:
      raise StorageNotPresentException("Storage %s not present" % name)

  def _make_folder_item(self, path, files):
    return {
      "#path": path,
      "#files": files
    }
  # override in child class
  def _add_storage(self, name: str, storage: dict, properties: ProviderProperties):
    pass

  def _update_storage(self, name: str, storage: dict, properties: ProviderProperties):
    pass

  def _get_storage(self, name: str, storage: dict, properties: ProviderProperties):
    return storage["data"]
