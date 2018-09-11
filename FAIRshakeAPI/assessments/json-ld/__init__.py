import extruct
import requests
from w3lib.html import get_base_url
from django.conf import settings
from objectpath import Tree

def bind(func, *args, **kwargs):
  def func_wrapper(*_args, **_kwargs):
    return func(*args, *_args, **kwargs, **_kwargs)
  return func_wrapper

def get_json_ld_attr(tree, attrs):
  def get_json_ld_attr_inner():
    for attr in attrs:
      attr_split = attr.split('.')
      for result in tree.execute(
        '$..*[@.@context is "http://schema.org"]..*[@.@type is {attr_type}].{attr_val}'.format(
          attr_type=attr_split[0],
          attr_val='.'.join(attr_split[1:]),
        )
      ):
        yield str(result)
  return ' '.join(get_json_ld_attr_inner())

to_schema = {
  'metric:77': [
    'WebSite.isAccessibleForFree', # CreativeWork
  ],
  # 'target:title': [
  # 'WebSite.name', # Thing
  # ],
  'metric:60': [
    'WebSite.name', # Thing
  ],
  # 'target:description': [
  # 'WebSite.description', # Thing
  # ],
  'metric:63': [
    'WebSite.description', # Thing
    'DataCatalog.description',
    'Dataset.description',
  ],
  'metric:21': [
    'WebSite.identifier', # Thing
    'DataCatalog.identifier',
    'Dataset.identifier',
  ],
  'metric:29': [
    'WebSite.license', # CreativeWork
    'DataCatalog.license',
    'Dataset.license',
  ],
  'metric:27': [
    'WebSite.contact', # CreativeWork
    'DataCatalog.contact',
    'Dataset.contact',
  ],
  'metric:38': [
    'WebSite.version', # CreativeWork
    'DataCatalog.version',
    'Dataset.version',
  ],
  # 'target:image': [
  # 'WebSite.image', # Thing
  # ],
  # 'target:type': [
  # 'WebSite.mainEntity', # CreativeWork
  # ],
  # 'target:tags': [
  # 'WebSite.keywords', # CreativeWork
  # ],
  'metric:77': [
    'WebSite.isAccessibleForFree', # CreativeWork
    'DataCatalog.isAccessibleForFree', # CreativeWork
    'Dataset.isAccessibleForFree', # CreativeWork
  ],
  'metric:36': [
    'WebSite.citation', # CreativeWork
    'DataCatalog.citation', # CreativeWork
    'Dataset.citation', # CreativeWork
  ],
  'metric:25': [
    'Dataset.url', # CreativeWork
  ],
}

class Assessment:
  inputs = [
    'target:url',
  ]
  outputs = [
    'metric:30',
  ] + list(to_schema.keys())

  @classmethod
  def perform(kls, inputs):
    url = inputs['target:url']
    r = requests.get(url)
    base_url = get_base_url(r.text, r.url)
    data = extruct.extract(r.text, base_url=base_url, syntaxes=['json-ld'])['json-ld']
    tree = Tree(data)
    results = {}

    return dict(
      **{
        'metric:30': {
          'answer': 'yes' if data else 'no',
        },
      },
      **{
        key: {
          'answer': 'yes' if attr else 'no',
          'comment': attr if attr else 'json-ld %s not found' % (' '.join(to_schema[key])),
        } if key.startswith('metric:') else attr
        for key, attr in zip(
          to_schema.keys(),
          map(
            bind(get_json_ld_attr, tree),
            to_schema.values()
          )
        )
      }
    )
