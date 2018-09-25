from rest_framework.views import exception_handler
from django.shortcuts import redirect
from django.urls import reverse

def handler(exc, context):
  response = exception_handler(exc, context)
  request = context['request']

  if all([
    'text/html' in request.META['HTTP_ACCEPT'],
    request.user.is_anonymous,
    response.status_code >= 400,
    response.status_code < 500,
  ]):
    return redirect(reverse('account_login') + '?next=' + request.get_full_path())

  return response
