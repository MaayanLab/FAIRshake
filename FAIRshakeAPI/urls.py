from django.urls import path, include
from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls
from . import views

router = routers.SimpleRouter()
router.register(r'answer', views.AnswerViewSet, base_name='answer')
router.register(r'assessment', views.AssessmentViewSet, base_name='assessment')
router.register(r'digital_object', views.DigitalObjectViewSet, base_name='digital_object')
router.register(r'metric', views.MetricViewSet, base_name='metric')
router.register(r'project', views.ProjectViewSet, base_name='project')
router.register(r'rubric', views.RubricViewSet, base_name='rubric')
router.register(r'score', views.ScoreViewSet, base_name='score')
router.register(r'digital_objects_to_rubrics', views.DigitalObjectsToRubricsViewSet, base_name='digital_objects_to_rubrics')
router.register(r'request_assessment', views.RequestAssessmentViewSet, base_name='request_assessment')

urlpatterns = [
    path('', include(router.urls)),
    path('', get_swagger_view(title='FAIRshake')),
    path('coreapi/', include_docs_urls(title='FAIRshake')),
    path('schema/', get_schema_view(title='FAIRshake')),
    path('auth/', include('rest_auth.urls')),
    path('auth/registration/', include('rest_auth.registration.urls')),
]
