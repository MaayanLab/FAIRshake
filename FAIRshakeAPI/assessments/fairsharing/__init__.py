from django.conf import settings
from scripts.pyswagger_wrapper import SwaggerClient

class Assessment:
  inputs = [
    'target:fairsharing'
  ]
  outputs = [
    'target:url',
    'target:description',
    'target:title',
    # 'target:doi',
    # 'target:authors'
    'metric:9', # license
    'metric:60', # title
    'metric:101', # taxonomies
    'metric:102', # domains
  ]
  @classmethod
  def perform(kls, inputs):
    client = SwaggerClient(
      'https://fairsharing.org/api/?format=openapi',
      headers={
        'Api-Key': settings.ASSESSMENT_CONFIG['fairsharing']['api-key'],
      }
    )
    results = client.actions.database_summary_read.call(
      bsg_id=inputs['target:fairsharing']
    )
    return {
      'target:url': results['data'].get('homepage'),
      'target:description': results['data'].get('description'),
      'target:title': results['data'].get('name'),
      # 'target:doi': results['data'].get('doi'),
      'metric:9': 'yes' if results['data'].get('license') else 'no',
      'metric:60': 'yes' if results['data'].get('homepage') is not None else 'no',
      'metric:101': 'yes' if results['data']['taxonomies'] else 'no',
      'metric:102': 'yes' if results['data']['domains'] else 'no',
      # 'target:authors': results['data'].get('maintainers'),
    }
