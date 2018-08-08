import json
from django import template

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
def limit_list(text, amount):
  return (''.join(text[:amount] if text[amount-1] != ' ' else text[:amount-1]) + '...' if len(text) > amount else text).split()