from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
  openapi.Info(
    title='FAIRshake API v2',
    default_version='v2',
    description='A web interface for the scoring of biomedical digital objects by user evaluation according to the FAIR data principles: Findability, Accessibility, Interoperability, and Reusability',
    terms_of_service='https://fairshake.cloud/',
    contact=openapi.Contact(
      email='avi.maayan@mssm.edu',
    ),
    license=openapi.License(name='Apache 2.0 License'),
  ),
  public=True,
  permission_classes=[permissions.AllowAny],
)
