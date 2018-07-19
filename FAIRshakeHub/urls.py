from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('bookmarklet/', views.bookmarklet, name='bookmarklet'),
    path('chrome_extension/', views.chrome_extension, name='chrome_extension'),
    path('projects/', views.projects, name='projects'),
    path('start_project/', views.start_project, name='start_project'),
    path('project/<str:project>/resources/', views.resources, name='resources'),
    path('project/<str:project>/my_evaluations/', views.my_evaluations, name='my_evaluations'),
    path('evaluation/', views.evaluation, name='evaluation'),
    path('evaluated_projects/', views.evaluated_projects, name='evaluated_projects'),
]
