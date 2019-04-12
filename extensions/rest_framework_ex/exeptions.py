import logging
from rest_framework.views import exception_handler
from django.shortcuts import redirect
from django.urls import reverse
from django.template.defaultfilters import urlencode

def handler(exc, context):
  response = exception_handler(exc, context)
  if not response:
    return response
  request = context['request']

  logging.debug('exception occured', request, response, exc)
  if all([
    'text/html' in request.META['HTTP_ACCEPT'],
    request.user.is_anonymous,
    response.status_code >= 400,
    response.status_code < 500,
  ]):
    return redirect(reverse('account_login') + '?next=' + urlencode(request.get_full_path()))

  return response
