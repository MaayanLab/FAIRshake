import json
from django import template
from django.contrib.auth.models import AnonymousUser

register = template.Library()

@register.filter
def return_item(l, i):
  try:
    return l[i]
  except:
    return None

@register.filter
def jsonify(d):
  return json.dumps(d)

@register.filter
def unslugify(v):
  return ' '.join(map(str.capitalize, v.split('_')))

@register.filter
def limit(text, amount):
  return ''.join(text[:amount]) + '...' if len(text) > amount else text

@register.filter
def as_path(req):
  if not req:
    return ''
  return '&'.join(map('='.join, req.items()))

@register.filter
def to_model(name):
  ''' Note: this is a dirty hack, we really should provide the model name to the context
  '''
  return {
    'digital_objects': 'digital_object',
    'authors': 'author',
    'rubrics': 'rubric',
    'metrics': 'metric',
    'projects': 'project',
    'digitalobject': 'digital_object',
    'target': 'digital_object',
    'rubric': 'rubric',
    'project': 'project',
  }.get(name, name)

@register.simple_tag(takes_context=True)
def select_template(context, *L):
  return template.loader.select_template(L).render(context.flatten())

@register.simple_tag(takes_context=True)
def has_permission(context, obj, perm):
  return obj.has_permission(
    context.get('user', AnonymousUser()),
    perm,
  )
