from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'answer', views.AnswerViewSet)
router.register(r'assessment', views.AssessmentViewSet)
router.register(r'author', views.AuthorViewSet)
router.register(r'digital_object', views.DigitalObjectViewSet)
router.register(r'metric', views.MetricViewSet)
router.register(r'project', views.ProjectViewSet)
router.register(r'rubric', views.RubricViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
