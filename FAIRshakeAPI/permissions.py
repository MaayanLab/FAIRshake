from rest_framework import permissions
from . import models

class IdentifiablePermissions(permissions.BasePermission):
  def has_object_permission(self, request, view, obj):
    if view.action == 'add':
      print(view.action)
      return request.user.is_authenticated()
    elif request.method in permissions.SAFE_METHODS and view.action not in ['modify', 'delete']:
      return True
    else:
      return obj.authors and obj.authors.filter(id=request.user.id).exists()

class AssessmentPermissions(permissions.BasePermission):
  def has_object_permission(self, request, view, obj):
    if view.action == 'add':
      return request.user.is_authenticated()
    elif request.method in permissions.SAFE_METHODS or view.action in ['modify', 'delete']:
      return True
    else:
      return obj.assessor == request.user

class AssessmentRequestPermissions(permissions.BasePermission):
  def has_object_permission(self, request, view, obj):
    if view.action == 'add':
      return request.user.is_authenticated()
    elif request.method in permissions.SAFE_METHODS or view.action not in ['modify', 'delete']:
      return True
    else:
      return obj.requestor == request.user
