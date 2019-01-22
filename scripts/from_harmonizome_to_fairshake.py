#!/usr/bin/env python3

# We create a `pyswagger_wrapper`, a `bravado`-inspired but `pyswagger`-based
#  Swagger Client library. It uses parsed swagger to generate python methods
#  for interacting with the API with docstrings and all.
# It makes working with swagger-described APIs easy.
import os
from pyswaggerclient import SwaggerClient
from merging import prompt_select_dups

# Configure API credentials for FAIRshake
#  FAIRshake allows you to get your API_KEY with your USERNAME
#  EMAIL, and PASSWORD if you don't know it currently.
# This script will find it if it isn't provided.

FAIRSHAKE_API_KEY = os.environ.get('FAIRSHAKE_API_KEY')
FAIRSHAKE_USERNAME = os.environ.get('FAIRSHAKE_USERNAME')
FAIRSHAKE_EMAIL = os.environ.get('FAIRSHAKE_EMAIL')
FAIRSHAKE_PASSWORD = os.environ.get('FAIRSHAKE_PASSWORD')

def harmonizome_get_all(harmonizome):
  ''' Get all the dataset names in Harmonizome through the
  database endpoint.
  
  Because this endpoint is paginated, we follow the `next`
   attribute if it is present until all databases have been
   yielded from the function.
  '''
  response = harmonizome.actions.dataset.call()
  while True:
    for dataset in response['entities']:
      yield dataset
    if not response['next']:
      break
    response = harmonizome.request(harmonizome._app.url + response['next'])

def harmonizome_obj_to_fairshake_obj(harmonizome_obj):
  ''' Convert a Harmonizome object entry into a FAIRshake
  object entry, mapping the field names in the Harmonizome
  object to those in FAIRshake.

  We'll store both the `homepage` url and the `doi` as a url.

  We'll also add this object to the Harmonizome project (id 64)
   and give it the JSON-LD rubric (id 20).
  '''
  harmonizome_obj_response = harmonizome.request(harmonizome_base_url + harmonizome_obj['href'])
  harmonizome_base_url = 'http://amp.pharm.mssm.edu/Harmonizome'
  return {
    "title": harmonizome_obj_response['name'],
    "description": harmonizome_obj_response['description'],
    "tags": "dcppc",
    "url": harmonizome_base_url + harmonizome_obj['href'],
    "projects": [
      64, # Harmonizome Project
    ],
    "rubrics": [
      20, # JSON-LD rubric
    ],
  }

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

def send_harmonizome_objects_to_fairshake(harmonizome=None, fairshake=None):
  ''' With fairshake and fairsharing swagger clients, we go through
  all the objects in fairsharing, convert the objects to fairshake objects,
  and then try to register those objects with fairshake.
  '''
  for harmonizome_obj in harmonizome_get_all(harmonizome):
    fairshake_obj = harmonizome_obj_to_fairshake_obj(harmonizome_obj)
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

def get_harmonizome_client(harmonizome_spec):
  ''' Create a swagger client for harmonizome.
  '''

  harmonizome = SwaggerClient(
    'https://raw.githubusercontent.com/MaayanLab/smartAPIs/master/harmonizome_smartapi.yml',
  )
  return harmonizome

def main():
  ''' Main function of this script. Establish connections to FAIRshake
  and to Harmonizome with the api keys, if necessary, and then send the harmonizome
  objects to fairshake.
  '''
  fairshake = get_fairshake_client(
    username=FAIRSHAKE_USERNAME,
    email=FAIRSHAKE_EMAIL,
    password=FAIRSHAKE_PASSWORD,
    api_key=FAIRSHAKE_API_KEY,
  )
  harmonizome = get_harmonizome_client()
  send_harmonizome_objects_to_fairshake(
    harmonizome=harmonizome,
    fairshake=fairshake,
  )

if __name__ == '__main__':
  main()
