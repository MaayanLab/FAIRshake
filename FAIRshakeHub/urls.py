from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('bookmarklet/', views.bookmarklet, name='bookmarklet'),
    path('chrome_extension/', views.chrome_extension, name='chrome_extension'),
    path('project/create/', views.project_create, name='project-create'),
    path('digital_object/create/', views.digital_object_create, name='digital_object-create'),
    path('rubric/create/', views.rubric_create, name='rubric-create'),
    path('metric/create/', views.metric_create, name='metric-create'),
    path('assessment/create/', views.assessment_create, name='assessment-create'),
    path('select2/', include('select2.urls')),
]
