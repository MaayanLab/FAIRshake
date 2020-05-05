from django.urls import path, re_path, include
from extensions.rest_framework_ex import routers
from rest_framework.documentation import include_docs_urls
from . import views

router = routers.CustomRouter()
router.register(r'assessment_request', views.AssessmentRequestViewSet, basename='assessment_request')
router.register(r'assessment', views.AssessmentViewSet, basename='assessment')
router.register(r'digital_object', views.DigitalObjectViewSet, basename='digital_object')
router.register(r'metric', views.MetricViewSet, basename='metric')
router.register(r'project', views.ProjectViewSet, basename='project')
router.register(r'rubric', views.RubricViewSet, basename='rubric')
router.register(r'score', views.ScoreViewSet, basename='score')

urlpatterns = [
  path('', include(router.urls)),
  path('coreapi/', include_docs_urls(title='FAIRshake')),
]
