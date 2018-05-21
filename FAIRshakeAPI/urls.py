from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'', views.APIViewSet)

urlpatterns = [
    path('auth/', include('rest_framework.urls'), name='auth'),
    path('docs/', views.docs, name='docs'),
    path('', include(router.urls)),
]
