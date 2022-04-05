from django import template
from django.conf import settings as settings_

register = template.Library()

@register.simple_tag
def settings(name):
  return getattr(settings_, name, "")
