#!/usr/bin/env python3

from pyswagger_wrapper import SwaggerClient

# Configure FAIRsharing api
FAIRSHARING_API_KEY = os.environ.get('FAIRSHARING_API_KEY')

# Configure FAIRshake api
FAIRSHAKE_API_KEY = os.environ.get('FAIRSHAKE_API_KEY')
# Or
FAIRSHAKE_USERNAME = os.environ.get('FAIRSHAKE_USERNAME')
FAIRSHAKE_PASSWORD = os.environ.get('FAIRSHAKE_PASSWORD')

def fairsharing_get_all(fairsharing):
  response = fairsharing.actions.database_summary_list.call()
  while response['next']:
    for database in response['results']:
      yield database
    response = fairsharing.request(response['next'])

def fairsharing_obj_to_fairshake_obj(fairsharing_obj):
  return {
    "title": fairsharing_obj['name'],
    "description": fairsharing_obj['description'],
    "tags": "dcppc",
    "url": '\n'.join([
      fairsharing_obj['homepage'],
      'https://doi.org/' + fairsharing_obj['doi'],
    ]),
    "projects": [
      14, # FAIRsharing project
    ],
    "rubrics": [
      19, # FAIRsharing rubric
    ],
  }

def register_fairshake_obj_if_not_exists(fairshake, fairshake_obj):
  existing = fairshake.actions.digital_object_list.call(
    title=fairshake_obj['title'],
  )['results'] + fairshake.actions.digital_object_list.call(
    url=fairshake_obj['url'],
  )['results']
  if existing:
    print('Similar objects were found')
    print(*existing, sep='\n')
  else:
    print('No similar objects were found')

  print('Object to add')
  print(fairshake_obj)
  print('Add this object? [y/N]')

  ans = input()
  if ans in ['y', 'Y']:
    obj = fairshake.actions.digital_object_create.call(data=fairshake_obj)
    print('Registered', obj, end='\n\n')
  else:
    print('Skipping.', end='\n\n')

if __name__ == '__main__':
  # Connect to fairshake
  fairshake = SwaggerClient(
    'https://fairshake.cloud/v2/swagger?format=openapi',
  )

  # Obtain authentication credentials if not present
  if not FAIRSHAKE_API_KEY:
    fairshake_auth = fairshake.actions.auth_login_create.call(data={
      'username': FAIRSHAKE_USERNAME,
      'password': FAIRSHAKE_PASSWORD,
    })
    FAIRSHAKE_API_KEY = fairshake_auth['key']

  # Update request headers
  fairshake.update(
    headers={
      'Authorization': 'Token ' + FAIRSHAKE_API_KEY,
    }
  )

  # Connect to fairsharing
  fairsharing = SwaggerClient(
    'https://fairsharing.org/api?format=openapi',
    headers={
      'Api-Key': FAIRSHARING_API_KEY,
    }
  )

  for fairsharing_obj in fairsharing_get_all():
    fairshake_obj = fairsharing_obj_to_fairshake_obj(fairsharing_obj)
    register_fairshake_obj_if_not_exists(fairshake_obj)
