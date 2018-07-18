from django.urls import path, include
from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls
from . import views

router = routers.DefaultRouter()
router.register(r'answer', views.AnswerViewSet)
router.register(r'assessment', views.AssessmentViewSet)
router.register(r'author', views.AuthorViewSet)
router.register(r'digital_object', views.DigitalObjectViewSet)
router.register(r'metric', views.MetricViewSet)
router.register(r'project', views.ProjectViewSet)
router.register(r'rubric', views.RubricViewSet)
router.register(r'score', views.ScoreViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('coreapi/', include_docs_urls(title='FAIRshake')),
    path('openapi/', get_swagger_view(title='FAIRshake')),
    path('schema/', get_schema_view(title='FAIRshake')),
]
