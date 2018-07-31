from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
  def has_object_permission(self, request, view, obj):
    '''
    Ensure user is a registered author of this digital object.
    '''
    if request.method in permissions.SAFE_METHODS:
      return True
    return not obj.authors.filter(id=request.user).empty()
