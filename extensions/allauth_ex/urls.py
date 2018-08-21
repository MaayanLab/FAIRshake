from django.urls import path, re_path, include
from . import views

urlpatterns = [
  path('', include('allauth.urls')),
  path('delete/', views.account_delete, name='account_delete'),
  path('registration/', include('rest_auth.registration.urls')),
  path('github/', views.GithubLogin.as_view(), name='github_auth'),
  path('orcid/', views.OrcidLogin.as_view(), name='orcid_auth'),
]
