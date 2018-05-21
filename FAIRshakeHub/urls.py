from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('bookmarklet/', views.bookmarklet, name='bookmarklet'),
    path('chrome_extension/', views.chrome_extension, name='chrome_extension'),
    path('register/', views.register, name='register'),
    path('projects/', views.projects, name='projects'),
    path('start_project/', views.start_project, name='start_project'),
    path('login/', views.login, name='login'),
]
