# TODO
# - SmartAPI Automated assessment
#   - Registration: title, description, tags, url(s)
#   - versioned
#   - contact
#   - all paths have unique operationId
#   - all paths/parameters/responses have descriptions, bonus for examples
#   - ToS
#   - https
#   - license
#   - access restriction
#   - x-url (smartAPI fields all described w/ x-type and x-description)

import re
import sys
import json
import itertools
from pyswaggerclient import SwaggerClient
from pyswaggerclient.fetch import read_spec
from objectpath import Tree

# import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FAIRshake.settings")
# import django
# django.setup()
# from FAIRshakeAPI import models

metrics = [
  {
    'query': '$..contact.email',
    'desc': 'Has contact',
    'metric': 27,
    'pattern': re.compile(r'.+@.+'),
  },
]

SmartAPI = SwaggerClient('https://smart-api.info/api/metadata/27a5b60716c3a401f2c021a5b718c5b1?format=yaml')

res = {}
for api in itertools.chain.from_iterable([
  SmartAPI.actions.query_get.call(q='openapi:3')['hits'],
  SmartAPI.actions.query_get.call(q='swagger:2')['hits'],
]):
  # Get it
  data = read_spec(api)
  # Parse it
  root = Tree(data)
  # Look for metrics
  answers = {}
  for metric in metrics:
    matches = root.execute(metric['query'])
    if metric['pattern']:
      results = ' '.join([e.strip() for e in matches]).strip()
    else:
      results = metric['query']
    answers[metric['desc']] = {
      'metric': metric.get('metric',''),
      'answer': 'yes' if matches and (metric['pattern'] is None or metric['pattern'].match(results)) else 'no',
      'comment': results,
    }

    res[data['info']['title']] = answers

print(res)
