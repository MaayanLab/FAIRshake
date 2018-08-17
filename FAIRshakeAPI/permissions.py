from rest_framework import permissions
from . import models

class ModelDefinedPermissions(permissions.BasePermission):
  ''' Allow models to define their own permissions
  '''

  def has_permission(self, request, view):
    if request.user.is_staff:
      return True
    if view.action in ['add', 'create']:
      return request.user.is_authenticated
    else:
      return request.method in permissions.SAFE_METHODS

  def has_object_permission(self, request, view, obj):
    if request.user.is_staff:
      return True
    else:
      return obj.has_object_permission(request, view)
