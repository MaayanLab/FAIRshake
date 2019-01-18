from django.urls import path, re_path, include
from . import views

urlpatterns = [
  path('', include('allauth.urls')),
  path('delete/', views.account_delete, name='account_delete'),
  path('api_access/', views.account_api_access, name='account_api_access'),
  path('github/', views.GithubLogin.as_view(), name='github_auth'),
  path('orcid/', views.OrcidLogin.as_view(), name='orcid_auth'),
  path('globus/', views.GlobusLogin.as_view(), name='globus_auth'),
]
