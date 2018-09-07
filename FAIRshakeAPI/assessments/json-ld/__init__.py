import extruct
import requests
from w3lib.html import get_base_url
from django.conf import settings
from objectpath import Tree

def get_json_ld_attr(tree, attr):
  attrs = attr.split('.')
  return tree.execute(
    '$..*[@.@context is "http://schema.org"]..*[@.@type is {attr_type}].{attr_val}'.format(
      attr_type=attrs[0],
      attr_val='.'.join(attrs[1:]),
    )
  )

class Assessment:
  inputs = [
    'target:url',
    'rubric',
  ]
  outputs = [ # TODO: ensure this gets run at least (and only) once
    'target',
    'metric',
  ]
  @classmethod
  def perform(kls, inputs):
    r = requests.get(inputs['target:url'])
    base_url = get_base_url(r.text, r.url)
    data = extruct.extract(r.text, base_url=base_url, syntaxes=['json-ld'])['json-ld']
    tree = Tree(data)
    results = {}

    for metric in inputs['rubric'].metrics.all():
      # TODO: add jsonld as metric attribute
      if getattr(metric, 'jsonld'):
        attr = get_json_ld_attr(tree, metric.jsonld)
        results['metric:%d' % (metric.id)] = {
          'answer': 'yes' if attr else 'no',
          'comment': attr,
        }

    return results
