from rest_framework import viewsets, permissions
from rest_framework_swagger.views import get_swagger_view
from .serializers import AssessmentSerializer
from .models import Assessment

docs = get_swagger_view(title='FAIRshakeAssessment')

# TODO: Manual assessment form

class AssessmentViewSet(viewsets.ModelViewSet):
    ''' Assessment Model interaction

    Authenticated users can:
        Register Assessments
    Anonymous users can:
        Query Assessments
    '''
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    queryset = Assessment.objects.all().order_by('-timestamp')
    serializer_class = AssessmentSerializer
