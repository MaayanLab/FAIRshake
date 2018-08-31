from django.views.generic import TemplateView
from django.conf.urls import url

from rest_auth.registration.views import RegisterView, VerifyEmailView
from .views import ConfirmEmailView

urlpatterns = [
    url(r'^$', RegisterView.as_view(), name='rest_register'),
    url(r'^verify-email/$', VerifyEmailView.as_view(), name='rest_verify_email'),
    url(r'^account-confirm-email/(?P<key>[-:\w]+)/$', ConfirmEmailView.as_view(),
        name='account_confirm_email'),
]
