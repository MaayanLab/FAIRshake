from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
  def has_object_permission(self, request, view, obj):
    '''
    Ensure user is a registered author of this digital object.
    '''
    if request.method in permissions.SAFE_METHODS:
      return True
    return obj.authors and obj.authors.filter(id=request.user.id).exists()

class HasAssessmentPermissions(permissions.BasePermission):
  def has_object_permission(self, request, view, obj):
    '''
    Ensure user has permissions for an assessment
    '''
    return any([
      # Read only access
      request.method in permissions.SAFE_METHODS and any([
        # Creator of the assessment target
        obj.target and obj.target.filter(authors__id=request.user.id).exists(),
        # Creator of the assessment project
        obj.project and obj.project.filter(authors__id=request.user.id).exists(),
        # Requestor of the assessment
        obj.requestor.id == request.user.id,
      ]),
      # Assessor themselves (read write access)
      obj.assessor.id == request.user.id,
    ])
