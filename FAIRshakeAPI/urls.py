from django.urls import path, re_path, include
from rest_framework import routers
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls
from . import views, routers

router = routers.CustomRouter()
router.register(r'assessment_request', views.AssessmentRequestViewSet, base_name='assessment_request')
router.register(r'assessment', views.AssessmentViewSet, base_name='assessment')
router.register(r'digital_object', views.DigitalObjectViewSet, base_name='digital_object')
router.register(r'metric', views.MetricViewSet, base_name='metric')
router.register(r'project', views.ProjectViewSet, base_name='project')
router.register(r'rubric', views.RubricViewSet, base_name='rubric')
router.register(r'score', views.ScoreViewSet, base_name='score')

urlpatterns = [
    path('', include(router.urls)),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', views.schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', views.schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui',),
    path('coreapi/', include_docs_urls(title='FAIRshake')),
    path('auth/', include('rest_auth.urls')),
    path('auth/registration/', include('rest_auth.registration.urls')),
    path('auth/github/', views.GithubLogin.as_view(), name='github_auth'),
    path('auth/orcid/', views.OrcidLogin.as_view(), name='orcid_auth'),
]
