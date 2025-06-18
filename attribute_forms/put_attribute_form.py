import argparse
import json
import os

from pprint import pprint
from sys import path

def main():

  # Parse the command line
  args = parse_command_line()

  # If the api_client path was not specified, get it from the script path
  if not args.api_client:
    try:
      args.api_client = os.path.dirname(os.path.realpath(__file__)).split('api_client')[0] + str('api_client')
    except:
      fail('Could not get the api_client path from the command. Please specify using --api_client / -a')

  # Import the api client
  path.append(args.api_client)
  try:
    from mosaic import Mosaic, Project, Store
  except:
    fail('Cannot find mosaic. Please set the --api_client / -a argument')
  api_store = Store(config_file = args.client_config)
  api_mosaic = Mosaic(config_file = args.client_config)

  # Build the json object
  attributes_json = []
  stored_attributes = []
  if args.required_attributes:
    attributes = args.required_attributes.split(',') if ',' in args.required_attributes else [args.required_attributes]
    for attribute_id in attributes:
      attributes_json.append({'attribute_id': int(attribute_id), 'type': 'required'})
      stored_attributes.append(int(attribute_id))
  if args.suggested_attributes:
    attributes = args.suggested_attributes.split(',') if ',' in args.suggested_attributes else [args.suggested_attributes]
    for attribute_id in attributes:
      attributes_json.append({'attribute_id': int(attribute_id), 'type': 'suggested'})
      stored_attributes.append(int(attribute_id))
  if args.optional_attributes:
    attributes = args.optional_attributes.split(',') if ',' in args.optional_attributes else [args.optional_attributes]
    for attribute_id in attributes:
      attributes_json.append({'attribute_id': int(attribute_id), 'type': 'optional'})
      stored_attributes.append(int(attribute_id))

  # Get all available attribute forms
  attribute_form_id = False
  for attribute_form in api_mosaic.get_attribute_forms()['data']:
    if str(attribute_form['id']) == str(args.attribute_form_id):

      # Update the form name
      name = args.name if args.name else attribute_form['name']
      attribute_form_id = int(attribute_form['id'])

      # Handle the attributes if the retain attribute flag is set
      if args.retain_existing_attributes:
        for attribute in attribute_form['attribute_form_attributes']:

          # If the attribute is in stored_attributes it was updated by the user, so it is already in the
          # json and can be ignored
          if int(attribute['attribute_id']) not in stored_attributes:
            attributes_json.append({'attribute_id': attribute['attribute_id'], 'type': attribute['type']})

  # Fail if the given attribute id does not exist
  if not attribute_form_id:
    fail('no attribute form with the given id')
  print('Updating attribute form: ', str(name), '...', sep = '', end = '')

  # Remove amy requested attributes from the form
  attributes = []
  if args.remove_attributes:
    attributes = args.remove_attributes.split(',') if ',' in args.remove_attributes else [args.remove_attributes]
  updated_attributes_json = []
  for attribute in attributes_json:
    if str(attribute['attribute_id']) not in attributes:
      updated_attributes_json.append(attribute)

  # Post an attribute form
  data = api_mosaic.put_attribute_form(attribute_form_id, name = name, attributes = updated_attributes_json)
  print('complete')

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')
  api_arguments = parser.add_argument_group('API Arguments')
  project_arguments = parser.add_argument_group('Project Arguments')
  required_arguments = parser.add_argument_group('Required Arguments')
  optional_arguments = parser.add_argument_group('Optional Arguments')
  display_arguments = parser.add_argument_group('Display Information')

  # Define the location of the api_client and the ini config file
  api_arguments.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  api_arguments.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

  # Required arguments
  required_arguments.add_argument('--attribute_form_id', '-i', required = True, metavar = 'string', help = 'The id of the attribute form to update')

  # Optional arguments
  optional_arguments.add_argument('--name', '-n', required = False, metavar = 'string', help = 'The name of the attribute form')
  optional_arguments.add_argument('--required_attributes', '-r', required = False, metavar = 'string', help = 'A comma separated list of the ids of all required attributes')
  optional_arguments.add_argument('--suggested_attributes', '-s', required = False, metavar = 'string', help = 'A comma separated list of the ids of all suggested attributes')
  optional_arguments.add_argument('--optional_attributes', '-o', required = False, metavar = 'string', help = 'A comma separated list of the ids of all optional attributes')
  optional_arguments.add_argument('--remove_attributes', '-m', required = False, metavar = 'string', help = 'A comma separated list of the ids of all attributes to be removed from the form')
  optional_arguments.add_argument('--retain_existing_attributes', '-re', required = False, action = 'store_true', help = 'If set, no existing attributes will be removed from the attribute form - only new ones will be added')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
