#!/usr/bin/env python3

# We create a `pyswagger_wrapper`, a `bravado`-inspired but `pyswagger`-based
#  Swagger Client library. It uses parsed swagger to generate python methods
#  for interacting with the API with docstrings and all.
# It makes working with swagger-described APIs easy.
from pyswagger_wrapper import SwaggerClient

# Configure API credentials for both FAIRshake and FAIRSharing
#  FAIRshake allows you to get your API_KEY with your USERNAME
#  EMAIL, and PASSWORD if you don't know it currently.
# This script will find it if it isn't provided.

FAIRSHAKE_API_KEY = os.environ.get('FAIRSHAKE_API_KEY')
FAIRSHAKE_USERNAME = os.environ.get('FAIRSHAKE_USERNAME')
FAIRSHAKE_EMAIL = os.environ.get('FAIRSHAKE_EMAIL')
FAIRSHAKE_PASSWORD = os.environ.get('FAIRSHAKE_PASSWORD')

### APIMATIC Flow
# def convert_api_spec_to_swagger2(api_spec):
#   ''' 
#     1. Download APIMATIC Python SDK from https://www.apimatic.io/apidocs/cgaas-api/v/1_0#/net-standard-library/getting-started
#     2. Create a free account -- basic auth needed to use APIMATIC API

#     Convert api spec from OpenAPI3 to Swagger2 for use with our Swagger client.
  
#   '''
#   from apimatic.apimatic_client import ApimaticClient
#   from apimatic.configuration import Configuration
#   from apimatic.models.api_description_format import APIDescriptionFormat
#   from apimatic.exceptions.validation_exception import ValidationException
#   from apimatic.exceptions.api_exception import APIException

#   basic_auth_user_name = 'alexjones4@deloitte.com'
#   basic_auth_password = 'Carolina25@'


#   client = ApimaticClient(basic_auth_user_name, basic_auth_password)

#   api_transformer_controller = client.api_transformer

#   format = APIDescriptionFormat.SWAGGER_20_JSON
#   description_url = 'https://raw.githubusercontent.com/MaayanLab/smartAPIs/master/harmonizome_smartapi.yml'


#   try:
#       result = api_transformer_controller.transform_using_url(format, description_url)
#   except ValidationException as e: 
#       print(e)
#   except APIException as e: 
#       print(e)

#   # Write converted swagger spec file
#   with open('swagger2.json', 'w') as outfile:
#     json.dump(result,outfile)

from subproccess import Popen, PIPE
import requests
import yaml
# pip install yamlordereddictloader
import yamlordereddictloader

def get_harmonizome_spec():
  spec_url = 'https://raw.githubusercontent.com/MaayanLab/smartAPIs/master/harmonizome_smartapi.yml'
  harmonizome_spec = requests.get(spec_url)
  # Write file so we can convert using api-spec-converter
  harmonizome_openapi_spec = 'harmonizome_openapi_spec_delete.yml'
  harmonizome_swagger2_spec = 'harmonizome_swagger2_spec_delete.json'
  with open(harmonizome_openapi_spec, 'w') as del_file:
    del_file.write(harmonizome_spec)
  
  # Test if spec is not swagger2
  # Load yaml file into dict
  with open(harmonizome_openapi_spec) as f1:
    harmonizome_yaml_data = yaml.load(f1, Loader=yamlordereddictloader.Loader)
  f1.close()
  # Get spec version number
  try:
    version = yaml_data['swagger']
  except KeyError:
    version = yaml_data['openapi']
  if int(version.split('.')[0]) > 2
    # Convert openapi3 to swagger2 using Popen
    process = Popen(
      [
        'api-spec-converter', '--from=openapi_3', '--to=swagger_2', harmonizome_openapi_spec],
        shell=True,
        stdout=PIPE,
        stderr=PIPE)
    stdout, stderr = process.communicate()
    json_data = json.loads(stdout)

    # Write swagger2.json file to be used in SwaggerClient
    with open(harmonizome_swagger2_spec_delete.json, 'w') as f2:
      json.dump(json_data, f2)
    f2.close()

  # return location of swagger2 spec
  return harmonizome_swagger2_spec
  


def harmonizome_get_all(harmonizome):
  ''' Get all the dataset names in Harmonizome through the
  database endpoint.
  
  Because this endpoint is paginated, we follow the `next`
   attribute if it is present until all databases have been
   yielded from the function.
  '''
  harmonizome_base_url = 'http://amp.pharm.mssm.edu/Harmonizome'
  response = harmonizome.actions.dataset.call()
  while True:
    for dataset in response['entities']:
      yield dataset
    if no response['next']:
      break
    response = harmonizome.request(harmonizome_base_url + response['next'])

def harmonizome_obj_to_fairshake_obj(harmonizome_obj):
  ''' Convert a Harmonizome object entry into a FAIRshake
  object entry, mapping the field names in the Harmonizome
  object to those in FAIRshake.

  We'll store both the `homepage` url and the `doi` as a url.

  We'll also add this object to the FAIRSharing project (id 14)
   and give it the FAIRSharing rubric (id 19).
  '''
  harmonizome_obj_response = harmonizome.request(harmonizome_base_url + harmonizome_obj['href'])
  harmonizome_base_url = 'http://amp.pharm.mssm.edu/Harmonizome'
  return {
    "title": harmonizome_obj_response['name'],
    "description": harmonizome_obj_response['description'],
    "tags": "dcppc",
    "url": harmonizome_base_url + harmonizome_obj['href'],
    "projects": [
      14, # Harmonizome project
    ],
    "rubrics": [
      20, # JSON-LD rubric
    ],
  }

def register_harmonizome_obj_if_not_exists(fairshake, fairshake_obj):
  ''' Register the FAIRshake object, first checking to see if it
  exists in the database. To do this we query the title and url separately
  and present any results to the user. The user is responsible for
  visually inspecting the entry and determining whether or not to add
  the object from Harmonizome into FAIRShake.

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
    'https://fairshake.cloud/v2/swagger?format=openapi',
  )
  if not api_key:
    fairshake_auth = fairshake.actions.auth_login_create.call(data={
      'username': username,
      'email': email,
      'password': password,
    })
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
  ''' Using the api_key, create an authenticated swagger client to harmonizome.
  '''
  # FAIRSharing expects an Api-Key in the request header for
  #  authenticated calls

  harmonizome = SwaggerClient(
    harmonizome_spec
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
  harm_spec = get_harmonizome_spec(
  )
  harmonizome = get_harmonizome_client(harm_spec
  )
  send_harmonizome_objects_to_fairshake(
    harmonizome=harmonizome,
    fairshake=fairshake,
  )

if __name__ == '__main__':
  main()
