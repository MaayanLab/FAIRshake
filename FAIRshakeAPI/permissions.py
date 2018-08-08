from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
  def has_object_permission(self, request, view, obj):
    '''
    Ensure user is a registered author of this digital object.
    '''
    return any([
      request.method in permissions.SAFE_METHODS,
      all([
        obj.authors,
        obj.authors.filter(id=request.user.id).exists(),
      ]),
    ])

class IsRequestorOrAssessorOrReadOnly(permissions.BasePermission):
  def has_object_permission(self, request, view, obj):
    '''
    Ensure user is a registered author of this digital object.
    '''
    return any([
      request.method in permissions.SAFE_METHODS,
      obj.requestor == request.user,
      obj.assessment.assessor == request.user,
    ])
