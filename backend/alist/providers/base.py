from abc import ABCMeta, abstractmethod


class BasePageProvide(object):
  __metaclass__ = ABCMeta
  """
    Base abstract provider which need to be inherited
  """

  def __init__(self):
    pass

  @abstractmethod
  def do(self, *args, **kwargs):
    pass
