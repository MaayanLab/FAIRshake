from rest_framework import viewsets, permissions
from rest_framework_swagger.views import get_swagger_view
from .serializers import APISerializer
from .models import API

docs = get_swagger_view(title='FAIRshakeAPI')

class APIViewSet(viewsets.ModelViewSet):
    ''' API Model interaction

    Authenticated users can:
        Register APIs
    Anonymous users can:
        Query APIS
    '''
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    queryset = API.objects.all().order_by('-updated')
    serializer_class = APISerializer
