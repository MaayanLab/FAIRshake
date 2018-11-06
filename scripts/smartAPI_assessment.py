import re
import sys
import json
import itertools
import numpy as np
from pyswaggerclient import SwaggerClient
from pyswaggerclient.fetch import read_spec
from objectpath import Tree

# import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FAIRshake.settings")
# import django
# django.setup()
# from FAIRshakeAPI import models

# function gets ratio of present parameters
def get_Ratio(ROOT, sample, n, u):
  r = None 
  if len(list(ROOT.execute(n))) != 0:
    total = 0
    for s in sample:
      res = list(ROOT.execute(s))
      if u == 'unique':
        res = np.unique(res)
      total = total + len(res)
    total = total/len(sample)    
    r = (total)/len(list(ROOT.execute(n)))
  return(r)

metrics = [
  {
    'query': '$..info.x-accessRestriction.name',
    'desc': 'access restriction', 
    'metric': 92,
    'pattern': re.compile(r'.+'),
  },
  {
    'query': '$..tags.name',
    'desc': 'tags', 
    'metric': 123,
    'pattern': re.compile(r'.+'),
  },
  {
    'query': '$..info.version',
    'desc': 'Has version information', 
    'metric': 26,
    'pattern': re.compile(r'.+'),
  },
  {
    'query': '$..contact.email',
    'desc': 'Has contact',
    'metric': 27,
    'pattern': re.compile(r'.+@.+'),
  },
  {
    'query': '$..info.license.name',
    'desc': 'License',
    'metric': 117,
    'pattern': re.compile(r'.+'),
  },

  {
    'query': '$..info.termsOfService',
    'desc': 'Usage Protocol/TOS',
    'metric':122,
    'pattern': re.compile(r'.+'),
  },
  {
    'query': '$..info.title',
    'desc': 'Has a title',
    'metric': 60,
    'pattern': re.compile(r'.+'),
  },
  {
    'query': '$..info.description',
    'desc': 'Has a description',
    'metric': 63,
    'pattern': re.compile(r'.+'),
  },
  {
    'query': '$..contact.name',
    'desc': 'Metadata specifies the creators',
    'metric': 61,
    'pattern': re.compile(r'.+'),
  },
  {
    'query': '$..paths..parameters.description',
    'ratio': [['$..paths..parameters[@.description is not None]'],'$..paths..parameters','all'], # ratio of those with descriptions
    'desc': 'All parameters have descriptions',
    'metric': 124,
    'pattern': re.compile(r'.+'),
  },
  {
    'query': '$..paths.description',
    'ratio': [['$..paths[@.description is not None]'],'$..paths','all'], # ratio of those with descriptions
    'desc': 'All paths have descriptions',
    'metric': 125,
    'pattern': re.compile(r'.+'),
  },
  {
    'query': 'map(values, $..paths..responses.*).*[@.description is not  None].description',
    'ratio': [['map(values, $..paths..responses.*).*[@.description is not  None].description'],'map(values, $..paths..responses.*)','all'], # ratio of those with descriptions
    'desc': 'All responses have descriptions',
    'metric': 126,
    'pattern': re.compile(r'.+'),
  },
  {
    'query': '$..paths..operationId',
    'ratio': [['$..paths..operationId'],'$..paths..operationId','unique'], # ratio of unique ids
    'desc': 'All paths have unique operation Ids',
    'metric': 127,
    'pattern': re.compile(r'.+'),
  },
  {
    'query': '$.."x-externalResources"[@."x-url"]',
    'ratio': [['$.."x-externalResources"[@."x-type" is not None]','$.."x-externalResources"[@."x-description" is not None]'],'$.."x-externalResources"[@."x-url" is not None]','all'],
    'desc': 'x-url (smartAPI fields all described w/ x-type and x-description)',
    'metric': 128,
    'pattern': re.compile(r'.+'),
  },
]


SmartAPI = SwaggerClient('https://smart-api.info/api/metadata/27a5b60716c3a401f2c021a5b718c5b1?format=yaml')

def get_all(**kwargs):
  n_results = 0
  while True:
    resp = SmartAPI.actions.query_get.call(**kwargs, **{'from': n_results})
    for hit in resp['hits']:
      n_results += 1
      yield hit
    if n_results >= resp['total']:
      break
    else:
      resp = SmartAPI.actions.query_get.call(**kwargs)

res = {}
for api in itertools.chain.from_iterable([
  get_all(q='openapi:3'), get_all(q='swagger:2')
]):
  # Get it
  data = read_spec(api)
  # Parse it
  root = Tree(data)
  # Look for metrics
  answers = {}
  for metric in metrics:
    matches = root.execute(metric['query'])
    results = []
    ratio = None
    if matches != None:
        matches = list(itertools.chain(matches))
        results = '; '.join([e.strip() for e in matches]).strip()
        try:
          ratio = get_Ratio(root , metric['ratio'][0],metric['ratio'][1],metric['ratio'][2],)
        except:
          pass
  
    if ratio == None:
      answers[metric['desc']] = {
        'metric': metric.get('metric',''),
        'answer': 'yes' if len(results)>0 and metric['pattern'].match(results) else 'no',
        'comment': results,
      }
    else:
        answers[metric['desc']] = {
        'metric': metric.get('metric',''),
        'answer':ratio,
        'comment': metric['desc'],
      }
    
    # add metrics that get an automatic 'yes' simply for being on smartAPI
    answers['Machine readable metadata'] = {
      'metric': 89,
      'answer': 'yes',
      'comment': 'Machine readable metadata exists'
    }
    answers['Established data repository'] = {
      'metric': 24,
      'answer': 'yes',
      'comment': 'Data is in an established data repository'
    }
    answers['Downloadable'] = {
      'metric': 25,
      'answer': 'yes',
      'comment': 'Data can be downloaded for free from the repository'
    }

  res[data['info']['title']] = answers

print(res.keys())
