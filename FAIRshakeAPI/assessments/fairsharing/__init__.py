import re
from django.conf import settings
from pyswaggerclient import SwaggerClient

url_re = re.compile(r'^https?://doi.org/(.+)$')

metric_to_attr = {
  'metric:9': 'licence',
  'metric:60': 'homepage',
  'metric:101': 'taxonomies',
  'metric:102': 'domains',
}

class Assessment:
  inputs = [
    'target:url'
  ]
  outputs = [
    # 'target:url',
    # 'target:description',
    # 'target:title',
    # 'target:authors'
  ] + list(metric_to_attr.keys())

  @classmethod
  def perform(kls, inputs):
    urls = inputs['target:url']
    dois = [m.group(1) for m in map(url_re.match, urls) if m]

    if dois:
      client = SwaggerClient(
        'https://fairsharing.org/api/?format=openapi',
        headers={
          'Api-Key': settings.ASSESSMENT_CONFIG['fairsharing']['api-key'],
        }
      )

      results = [
        result
        for doi in dois
        for result in client.actions.database_summary_list.call(
          doi=doi,
        )['results']
      ]

      if len(results) > 1:
        logging.warn('More than 1 DOI was identified in the fairsharing database! (%s)' % (url))
      if len(results) >= 1:
        data = results[0]
      else:
        data = None
    else:
      data = None

    return {
      key: {
        'answer': 'yes' if data.get(attr) else 'no',
        'comment': data.get(attr),
      }
      for key, attr in metric_to_attr.items()
    } if data else {key: {} for key in metric_to_attr.keys()}
