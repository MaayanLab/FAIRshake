from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('bookmarklet/', views.bookmarklet, name='bookmarklet'),
    path('chrome_extension/', views.chrome_extension, name='chrome_extension'),
]
