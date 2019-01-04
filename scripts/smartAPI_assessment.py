import os
import re
import itertools
from pyswaggerclient import SwaggerClient
from pyswaggerclient.fetch import read_spec
from objectpath import Tree
from merging import prompt_merge_attr, prompt_select_dups

# Configure API credentials for FAIRshake
#  FAIRshake allows you to get your API_KEY with your USERNAME
#  EMAIL, and PASSWORD if you don't know it currently.
# This script will find it if it isn't provided.

FAIRSHAKE_API_KEY = os.environ.get('FAIRSHAKE_API_KEY')
FAIRSHAKE_USERNAME = os.environ.get('FAIRSHAKE_USERNAME')
FAIRSHAKE_EMAIL = os.environ.get('FAIRSHAKE_EMAIL')
FAIRSHAKE_PASSWORD = os.environ.get('FAIRSHAKE_PASSWORD')

# Rubric we'll be evaluating (smartapi)
rubric = 28

# Project we'll be evaluating (smartapi)
project = 53

# Metrics we'll be evaluating
# query: objectpath query
# desc: Description of the metric
# metric: The id of the metric we're evaluating
# pattern: valid content of query result
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
  {
    'metric': 89,
    'answer': 1.0,
    'desc': 'Machine readable metadata exists'
  },
  {
    'metric': 24,
    'answer': 1.0,
    'desc': 'Data is in an established data repository'
  },
  {
    'metric': 25,
    'answer': 1.0,
    'desc': 'Data can be downloaded for free from the repository'
  }
]

def smartapi_obj_to_fairshake_obj(smartapi_obj):
  ''' Convert a smartapi object entry into a FAIRshake
  object entry, mapping the field names in the smartapi
  object to those in FAIRshake.
  '''
  return {
    "title": smartapi_obj['info']['title'],
    "description": smartapi_obj['info'].get('description', ''),
    "tags": ','.join([t['name'] for t in smartapi_obj.get('tags', '')]),
    "url": '\n'.join(
      map(''.join,
        itertools.product(
          smartapi_obj['schemes'],
          ['://'],
          [smartapi_obj['host']],
          list(set(['', smartapi_obj['basePath']])),
        )
      )
    ),
    "projects": [project],
    "rubrics": [rubric],
  }

def get_ratio(ROOT, sample, n, u):
  '''
  function gets ratio of present parameters
  '''
  r = None
  if len(list(ROOT.execute(n))) != 0:
    total = 0
    for s in sample:
      res = list(ROOT.execute(s))
      if u == 'unique':
        res = list(set(res))
      total = total + len(res)
    total = total/len(sample)    
    r = (total)/len(list(ROOT.execute(n)))
  return(r)

def smartapi_get_all(smartapi, **kwargs):
  '''
  Yield paginated query operation using `from` syntax.

    query(from=0) == {
      [...] first 10
    }
    query(from=10) == {
      [...] second 10
    }
    ...
  '''
  n_results = 0
  while True:
    resp = smartapi.actions.query_get.call(**kwargs, **{'from': n_results})
    for hit in resp['hits']:
      n_results += 1
      yield hit
    if n_results >= resp['total']:
      break
    else:
      resp = smartapi.actions.query_get.call(**kwargs)

def get_fairshake_client(api_key=None, username=None, email=None, password=None):
  ''' Using either the api_key directly, or with fairshake
  user credentials, create an authenticated swagger client to fairshake.
  '''
  fairshake = SwaggerClient(
    'https://fairshake.cloud/swagger?format=openapi',
  )
  if not api_key:
    fairshake_auth = fairshake.actions.auth_login_create.call(data=dict({
      'username': username,
      'password': password,
    }, **({'email': email} if email else {})))
    api_key = fairshake_auth['key']
  # FAIRshake expects a Token in the Authorization request header for
  #  authenticated calls
  fairshake.update(
    headers={
      'Authorization': 'Token ' + api_key,
    }
  )
  return fairshake

def get_smartapi_client():
  ''' Create a swagger client for smartapi.
  '''
  smartapi = SwaggerClient('https://smart-api.info/api/metadata/27a5b60716c3a401f2c021a5b718c5b1?format=yaml')
  return smartapi

def register_fairshake_obj_if_not_exists(fairshake, fairshake_obj):
  ''' Register the FAIRshake object, first checking to see if it
  exists in the database. To do this we query the title and url separately
  and present any results to the user. The user is responsible for
  visually inspecting the entry and determining whether or not to add
  the object into FAIRShake.

  We prompt the user (defaulting to NOT add the object) and call the
  FAIRShake digital_object_create api endpoint if they do choose to register
  the object.
  '''
  try:
    existing = fairshake.actions.digital_object_list.call(
      title=fairshake_obj['title'],
    )['results'] + fairshake.actions.digital_object_list.call(
      url=fairshake_obj['url'],
    )['results']
  except:
    existing = []

  for result in prompt_select_dups(*existing, fairshake_obj):
    if result.get('id'):
      print('Updating %s...' % (str(result['id'])))
      id = result['id']
      del result['id']
      try:
        fairshake.actions.digital_object_update.call(id=id, data=result)
      except:
        pass
    else:
      print('Creating...')
      if result.get('id') is not None:
        del result['id']
      obj = fairshake.actions.digital_object_create.call(data=result)
      id = obj['id']
  return id

def assess_smartapi_obj(smartapi_obj):
  ''' Given a smartapi object from the API, assess it for its fairness
  '''
  root = Tree(smartapi_obj)
  print('Performing assessment...')

  answers = {}
  for metric in metrics:
    if metric.get('query') is None:
      answers[metric['desc']] = {
        'metric': metric.get('metric', ''),
        'answer': metric.get('answer', 1.0),
        'comment': metric['desc'],
      }
    else:
      matches = root.execute(metric['query'])
      results = []
      ratio = None
      if matches != None:
          matches = list(itertools.chain(matches))
          results = '; '.join([e.strip() for e in matches]).strip()
          try:
            ratio = get_ratio(
              root,
              metric['ratio'][0],
              metric['ratio'][1],
              metric['ratio'][2],
            )
          except:
            pass
    
      if ratio == None:
        answers[metric['desc']] = {
          'metric': metric.get('metric',''),
          'answer': 1.0 if len(results)>0 and metric['pattern'].match(results) else 0.0,
          'comment': str(results),
        }
      else:
        answers[metric['desc']] = {
          'metric': metric.get('metric',''),
          'comment': metric['desc'],
        }
        answers[metric['desc']]['answer'] = ratio

  return answers

def register_fairshake_assessment(fairshake, answers=None, project=None, rubric=None, target=None):
  ''' Register the assessment if it hasn't yet been registered.
  '''
  print('Registering assessment...', answers)
  try:
    assessment_id = fairshake.actions.assessment_list.call(
      project=project,
      target=target,
      rubric=rubric,
      methodology='auto',
    )['results'][0]['id']
  except:
    assessment_id = None
  if assessment_id:
    print('Updating assessment...')
    try:
      assessment_id = fairshake.actions.assessment_update.call(
        id=assessment_id,
        data=dict(
          project=project,
          target=target,
          rubric=rubric,
          answers=answers,
          methodology='auto',
        )
      )
    except:
      pass
  else:
    print('Creating assessment...')
    assessment_id = fairshake.actions.assessment_create.call(
      data=dict(
        project=project,
        target=target,
        rubric=rubric,
        answers=answers,
        methodology='auto',
      )
    )

  return assessment_id

def register_and_assess_all_smartapi_objects(smartapi=None, fairshake=None):
  ''' Gather all smartapi objects using `read_spec` to ensure they all
  follow the same smartapi format. Register them in FAIRshake and then
  assess them.
  '''
  for smartapi_obj in map(read_spec, itertools.chain(
    smartapi_get_all(smartapi, q='openapi:3'),
    smartapi_get_all(smartapi, q='swagger:2'),
  )):
    fairshake_obj = smartapi_obj_to_fairshake_obj(smartapi_obj)
    fairshake_obj_id = register_fairshake_obj_if_not_exists(fairshake, fairshake_obj)
    fairshake_assessment = assess_smartapi_obj(smartapi_obj)
    assessment_result = register_fairshake_assessment(fairshake,
      answers=[
        answer
        for answer in fairshake_assessment.values()
        if answer.get('answer') is not None
      ],
      project=project,
      rubric=rubric,
      target=fairshake_obj_id,
    )
    print(assessment_result)

def main():
  ''' Main function of this script. Establish connections to FAIRshake
  and to SmartAPI with the api keys, if necessary, and then send evaluate
  the smartAPI objects with FAIRshake
  '''
  fairshake = get_fairshake_client(
    username=FAIRSHAKE_USERNAME,
    email=FAIRSHAKE_EMAIL,
    password=FAIRSHAKE_PASSWORD,
    api_key=FAIRSHAKE_API_KEY,
  )
  smartapi = get_smartapi_client()

  register_and_assess_all_smartapi_objects(
    smartapi=smartapi,
    fairshake=fairshake,
  )

if __name__ == '__main__':
  main()
