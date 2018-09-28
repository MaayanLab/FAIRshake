#!/usr/bin/env python3

# We create a `pyswagger_wrapper`, a `bravado`-inspired but `pyswagger`-based
#  Swagger Client library. It uses parsed swagger to generate python methods
#  for interacting with the API with docstrings and all.
# It makes working with swagger-described APIs easy.
import os
from pyswagger_wrapper import SwaggerClient
from merging import prompt_merge_attr, prompt_select_dups

# Configure API credentials for both FAIRshake and FAIRSharing
#  FAIRshake allows you to get your API_KEY with your USERNAME
#  EMAIL, and PASSWORD if you don't know it currently.
# This script will find it if it isn't provided.
FAIRSHARING_API_KEY = os.environ.get('FAIRSHARING_API_KEY')
FAIRSHAKE_API_KEY = os.environ.get('FAIRSHAKE_API_KEY')
FAIRSHAKE_USERNAME = os.environ.get('FAIRSHAKE_USERNAME')
FAIRSHAKE_EMAIL = os.environ.get('FAIRSHAKE_EMAIL')
FAIRSHAKE_PASSWORD = os.environ.get('FAIRSHAKE_PASSWORD')

def fairsharing_get_all(fairsharing):
  ''' Get all the databases in FAIRSharing through the
  database_summary_list endpoint.
  
  Because this endpoint is paginated, we follow the `next`
   attribute if it is present until all databases have been
   yielded from the function.
  '''
  response = fairsharing.actions.database_summary_list.call()
  while True:
    for database in response['results']:
      yield database
    if not response['next']:
      break
    response = fairsharing.request(response['next'])

def fairsharing_obj_to_fairshake_obj(fairsharing_obj):
  ''' Convert a FAIRSharing object entry into a FAIRshake
  object entry, mapping the field names in the FAIRSharing
  object to those in FAIRshake.

  We'll store both the `homepage` url and the `doi` as a url.

  We'll also add this object to the FAIRSharing project (id 14)
   and give it the FAIRSharing rubric (id 19).
  '''
  return {
    "title": fairsharing_obj['name'],
    "description": fairsharing_obj['description'],
    "tags": "dcppc",
    "url": '\n'.join([
      fairsharing_obj['homepage']
    ] + (
      ['https://doi.org/' + fairsharing_obj['doi']] if fairsharing_obj.get('doi') else []
    )),
    "projects": [
      14, # FAIRsharing project
    ],
    "rubrics": [
      19, # FAIRsharing rubric
    ],
  }

def register_fairshake_obj_if_not_exists(fairshake, fairshake_obj):
  ''' Register the FAIRshake object, first checking to see if it
  exists in the database. To do this we query the title and url separately
  and present any results to the user. The user is responsible for
  visually inspecting the entry and determining whether or not to add
  the object from FAIRSharing into FAIRShake.

  We prompt the user (defaulting to NOT add the object) and call the
  FAIRShake digital_object_create api endpoint if they do choose to register
  the object.
  '''
  existing = fairshake.actions.digital_object_list.call(
    title=fairshake_obj['title'],
  )['results'] + fairshake.actions.digital_object_list.call(
    url=fairshake_obj['url'],
  )['results']

  for result in prompt_select_dups(*existing, fairshake_obj):
    if result.get('id'):
      print('Updating %s...' % (str(result['id'])))
      id = result['id']
      del result['id']
      fairshake.actions.digital_object_update.call(id=id, data=result)
    else:
      print('Creating...')
      if result.get('id') is not None:
        del result['id']
      fairshake.actions.digital_object_create.call(data=result)

def send_fairsharing_objects_to_fairshake(fairsharing=None, fairshake=None):
  ''' With fairshake and fairsharing swagger clients, we go through
  all the objects in fairsharing, convert the objects to fairshake objects,
  and then try to register those objects with fairshake.
  '''
  for fairsharing_obj in fairsharing_get_all(fairsharing):
    fairshake_obj = fairsharing_obj_to_fairshake_obj(fairsharing_obj)
    register_fairshake_obj_if_not_exists(fairshake, fairshake_obj)

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

def get_fairsharing_client(api_key):
  ''' Using the api_key, create an authenticated swagger client to fairsharing.
  '''
  # FAIRSharing expects an Api-Key in the request header for
  #  authenticated calls
  fairsharing = SwaggerClient(
    'https://fairsharing.org/api?format=openapi',
    headers={
      'Api-Key': api_key,
    }
  )
  return fairsharing

def main():
  ''' Main function of this script. Establish connections to FAIRshake
  and to FAIRSharing with the api keys and then send the fairsharing
  objects to fairshake.
  '''
  fairshake = get_fairshake_client(
    username=FAIRSHAKE_USERNAME,
    email=FAIRSHAKE_EMAIL,
    password=FAIRSHAKE_PASSWORD,
    api_key=FAIRSHAKE_API_KEY,
  )
  fairsharing = get_fairsharing_client(
    api_key=FAIRSHARING_API_KEY,
  )
  send_fairsharing_objects_to_fairshake(
    fairsharing=fairsharing,
    fairshake=fairshake,
  )

if __name__ == '__main__':
  main()
