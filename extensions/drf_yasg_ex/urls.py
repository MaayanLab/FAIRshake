from django.urls import path, re_path, include
from . import views

urlpatterns = [
  path('', views.schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui',),
  re_path(r'^swagger(?P<format>\.json|\.yaml)$', views.schema_view.without_ui(cache_timeout=0), name='schema-json'),
]
