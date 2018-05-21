from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.InsigniaAPI.as_view(), name='insignia'),
    path('docs/', views.docs),
]
