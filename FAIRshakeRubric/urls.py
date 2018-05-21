from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'rubric', views.RubricViewSet)
router.register(r'question_group', views.QuestionGroupViewSet)
router.register(r'question', views.QuestionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('docs/', views.docs),
]
