from django.urls import path, re_path, include
from rest_framework import routers
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
  path('coreapi/', include_docs_urls(title='FAIRshake')),
]
