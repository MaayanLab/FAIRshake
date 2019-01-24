import os
import re
import itertools
from pyswaggerclient import SwaggerClient
from objectpath import Tree
from merging import prompt_select_dups

# Configure API credentials for FAIRshake
#  FAIRshake allows you to get your API_KEY with your USERNAME
#  EMAIL, and PASSWORD if you don't know it currently.
# This script will find it if it isn't provided.

FAIRSHAKE_API_KEY = os.environ.get('FAIRSHAKE_API_KEY')
FAIRSHAKE_USERNAME = os.environ.get('FAIRSHAKE_USERNAME')
FAIRSHAKE_EMAIL = os.environ.get('FAIRSHAKE_EMAIL')
FAIRSHAKE_PASSWORD = os.environ.get('FAIRSHAKE_PASSWORD')

# Rubric we'll be evaluating (fairmetrics)
rubric = 25

# Project we'll be evaluating (dockstore)
project = 69

# Example metadata:
# {'aliases': [],
#  'author': 'Francesco Favero',
#  'checker_url': '',
#  'contains': [],
#  'description': '![](https://bytebucket.org/sequenza_tools/icons/raw/da034ccc8c1ab5f5f8e020402267bd3f2dd5d361/svg/sequenza_tools/sequenzaalpha_150.svg)\n\n![build_status](https://img.shields.io/docker/build/sequenza/sequenza.svg)\n![docker_pulls](https://img.shields.io/docker/pulls/sequenza/sequenza.svg)\n![docker_builds](https://img.shields.io/docker/automated/sequenza/sequenza.svg)\n\n**Sequenza workflow**\n\nAllele-specific SCNA analysis from tumor/normal sequencing with the sequenza docker container',
#  'has_checker': False,
#  'id': 'registry.hub.docker.com/sequenza/sequenza',
#  'meta_version': '2018-08-15 07:46:18.076',
#  'organization': 'sequenza',
#  'signed': False,
#  'toolclass': {'description': 'CommandLineTool',
#   'id': '0',
#   'name': 'CommandLineTool'},
#  'toolname': 'sequenza',
#  'url': 'https://dockstore.org/api/api/ga4gh/v2/tools/registry.hub.docker.com%2Fsequenza%2Fsequenza',
#  'verified': False,
#  'verified_source': '[]',
#  'versions': [{'containerfile': True,
#    'descriptor_type': ['CWL', 'WDL'],
#    'id': 'registry.hub.docker.com/sequenza/sequenza:2.2.0.9000',
#    'image': '',
#    'image_name': 'registry.hub.docker.com/sequenza/sequenza',
#    'meta_version': 'Thu Jan 01 00:00:00 UTC 1970',
#    'name': '2.2.0.9000',
#    'registry_url': 'registry.hub.docker.com',
#    'url': 'https://dockstore.org/api/api/ga4gh/v2/tools/registry.hub.docker.com%2Fsequenza%2Fsequenza/versions/2.2.0.9000',
#    'verified': False,
#    'verified_source': ''},
#   {'containerfile': True,
#    'descriptor_type': ['CWL', 'WDL'],
#    'id': 'registry.hub.docker.com/sequenza/sequenza:latest',
#    'image': '',
#    'image_name': 'registry.hub.docker.com/sequenza/sequenza',
#    'meta_version': 'Thu Jan 01 00:00:00 UTC 1970',
#    'name': 'latest',
#    'registry_url': 'registry.hub.docker.com',
#    'url': 'https://dockstore.org/api/api/ga4gh/v2/tools/registry.hub.docker.com%2Fsequenza%2Fsequenza/versions/latest',
#    'verified': False,
#    'verified_source': ''}

# Measurements:
metrics = [
  {
    'query': '$..id',
    'desc': 'globally unique identifier', 
    'metric': 104,
    'pattern': re.compile(r'.+'),
    'answer': 0.5,
  },
  {
    'query': '$..id',
    'desc': 'persistent identifier', 
    'metric': 105,
    'pattern': re.compile(r'.+'),
    'answer': 0.5,
  },
  {
    'desc': 'machine readable metadata', 
    'metric': 106,
    'answer': 1,
  },
  {
    'query': '$.author',
    'desc': 'standardized metadata',
    'metric': 107,
    'pattern': re.compile(r'.+'),
    'answer': 0.5,
  },
  {
    'query': '$..id',
    'desc': 'resource identifier',
    'metric': 108,
    'pattern': re.compile(r'.+'),
  },
  {
    'query': '$..url',
    'desc': 'resource discovery',
    'metric': 109,
    'pattern': re.compile(r'.+'),
  },
  {
    'desc': 'open, free, standardized access protocol',
    'metric': 110,
    'answer': 1,
    'comment': 'docker',
  },
  {
    'desc': 'protocol to access restricted content',
    'metric': 111,
    'answer': None,
  },
  {
    'desc': 'persistence of resource and metadata',
    'metric': 112,
    'answer': 0.5,
  },
  {
    'query': '$..@context',
    'desc': 'formal language',
    'metric': 113,
  },
  {
    'query': '$..@context.@vocab',
    'desc': 'fair vocab',
    'metric': 114,
  },
  {
    'query': '$..versions',
    'desc': 'linked',
    'metric': 115,
    'pattern': re.compile(r'.+'),
  },
  {
    'desc': 'digital resource license',
    'metric': 116,
    'answer': 0,
  },
  {
    'query': '$..license',
    'desc': 'metadata license',
    'metric': 117,
  },
  {
    'desc': 'provenance scheme',
    'metric': 118,
    'answer': 0,
  },
  {
    'desc': 'certificate of compliance',
    'metric': 119,
    'answer': 0,
  }
]

def dockstore_obj_to_fairshake_obj(dockstore_obj):
  ''' Convert a dockstore object entry into a FAIRshake
  object entry, mapping the field names in the dockstore
  object to those in FAIRshake.
  '''
  return {
    "title": dockstore_obj['toolname'],
    "description": dockstore_obj['description'].rstrip('\n'),
    "tags": ','.join([t['name'] for t in dockstore_obj.get('tags', '')]),
    "url": dockstore_obj['url'],
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

def dockstore_get_all(dockstore, **kwargs):
  '''
  Get all dockstore tools
  '''
  return dockstore.actions.toolsGet.call(**kwargs)

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

def get_dockstore_client():
  ''' Create a swagger client for dockstore.
  '''
  dockstore = SwaggerClient('https://dockstore.org/swagger.json')
  return dockstore

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

def assess_dockstore_obj(dockstore_obj):
  ''' Given a dockstore object from the API, assess it for its fairness
  '''
  root = Tree(dockstore_obj)
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
          results = '; '.join([str(e).strip() for e in matches]).strip()
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

def register_and_assess_all_dockstore_objects(dockstore=None, fairshake=None):
  ''' Gather all dockstore objects using `read_spec` to ensure they all
  follow the same dockstore format. Register them in FAIRshake and then
  assess them.
  '''
  for dockstore_obj in dockstore_get_all(dockstore):
    fairshake_obj = dockstore_obj_to_fairshake_obj(dockstore_obj)
    fairshake_obj_id = register_fairshake_obj_if_not_exists(fairshake, fairshake_obj)
    fairshake_assessment = assess_dockstore_obj(dockstore_obj)
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
  and to Dockstore with the api keys, if necessary, and then send evaluate
  the Dockstore objects with FAIRshake
  '''
  fairshake = get_fairshake_client(
    username=FAIRSHAKE_USERNAME,
    email=FAIRSHAKE_EMAIL,
    password=FAIRSHAKE_PASSWORD,
    api_key=FAIRSHAKE_API_KEY,
  )
  dockstore = get_dockstore_client()

  register_and_assess_all_dockstore_objects(
    dockstore=dockstore,
    fairshake=fairshake,
  )

if __name__ == '__main__':
  main()
