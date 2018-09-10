from versions.models import Versionable, VersionManager
from versions.fields import VersionedForeignKey, VersionedManyToManyField

class VersionManagerEx(VersionManager):
  use_in_migrations = True

class VersionableEx(Versionable):
  objects = VersionManagerEx()

  class Meta:
    abstract = True
