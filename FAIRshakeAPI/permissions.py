from rest_framework import permissions
from . import models

class ModelDefinedPermissions(permissions.BasePermission):
  ''' Allow models to define their own permissions
  '''

  def has_permission(self, request, view):
    return view.get_model().has_permission(None, request.user, view.action)

  def has_object_permission(self, request, view, obj):
    return obj.has_permission(request.user, view.action)
