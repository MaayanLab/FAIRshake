from django.conf import settings
from scripts.pyswagger_wrapper import SwaggerClient

class Assessment:
  inputs = [
    'target:fairsharing'
  ]
  outputs = [
    # 'target:url',
    # 'target:description',
    # 'target:title',
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
      # 'target:url': {
      #   'answer': results['data'].get('homepage'),
      #   'comment': results['data'].get('homepage'),
      # },
      # 'target:description': {
      #   'answer': results['data'].get('description'),
      #   'comment': results['data'].get('description'),
      # },
      # 'target:title': {
      #   'answer': results['data'].get('name'),
      #   'comment': results['data'].get('name'),
      # },
      'metric:9': {
        'answer': 'yes' if results['data'].get('licence') else 'no',
        'comment': results['data'].get('licence'),
      },
      'metric:60': {
        'answer': 'yes' if results['data'].get('homepage') is not None else 'no',
        'comment': results['data'].get('homepage'),
      },
      'metric:101': {
        'answer': 'yes' if results['data'].get('taxonomies') else 'no',
        'comment': results['data'].get('taxonomies'),
      },
      'metric:102': {
        'answer': 'yes' if results['data'].get('domains') else 'no',
        'comment': results['data'].get('domains'),
      },
      # 'target:doi': results['data'].get('doi'),
      # 'target:authors': results['data'].get('maintainers'),
    }
