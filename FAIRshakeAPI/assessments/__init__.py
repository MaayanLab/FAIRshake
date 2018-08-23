import pkgutil, importlib
from . import base

__path__ = pkgutil.extend_path(__path__, __name__)
for importer, modname, ispkg in pkgutil.walk_packages(path=__path__, prefix=__name__+'.'):
  mod = importlib.import_module(modname, __package__)
  if mod is not base:
    if getattr(mod, 'Assessment') is not None:
      mod.Assessment.__name__ = modname
      base.assessments.append(mod.Assessment)

from .base import Assessment
__all__ = ["Assessment"]
