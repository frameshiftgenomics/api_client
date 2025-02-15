import argparse
import json
import os

from pprint import pprint
from sys import path

def main():

  # Parse the command line
  args = parse_command_line()

  # If the api_client path was not specified, get it from the script path
  try:
    args.api_client = os.path.dirname(os.path.realpath(__file__)).split('api_client')[0] + str('api_client')
  except:
    fail('Could not get the api_client path from the command. Please specify using --api_client / -a')

  # Import the api client
  path.append(args.api_client)
  from mosaic import Mosaic, Project, Store
  api_store = Store(config_file = args.client_config)
  api_mosaic = Mosaic(config_file = args.client_config)

  # Build the json object
  attributes_json = []
  stored_attributes = []
  if args.required_attributes:
    attributes = args.required_attributes.split(',')
    for attribute_id in attributes:
      attributes_json.append({'attribute_id': int(attribute_id), 'type': 'required'})
      stored_attributes.append(int(attribute_id))
  if args.suggested_attributes:
    attributes = args.suggested_attributes.split(',')
    for attribute_id in attributes:
      attributes_json.append({'attribute_id': int(attribute_id), 'type': 'suggested'})
      stored_attributes.append(int(attribute_id))
  if args.optional_attributes:
    attributes = args.optional_attributes.split(',')
    for attribute_id in attributes:
      attributes_json.append({'attribute_id': int(attribute_id), 'type': 'optional'})
      stored_attributes.append(int(attribute_id))

  # Get all available attribute forms
  attribute_form_id = False
  attribute_form_name = False
  for attribute_form in api_mosaic.get_attribute_forms()['data']:
    if str(attribute_form['id']) == str(args.attribute_form_id):

      # Update the form name
      name = args.name if args.name else attribute_form['name']

      # Handle the attributes
      attribute_form_id = int(attribute_form['id'])
      attribute_form_name = attribute_form['name']
      for attribute in attribute_form['attribute_form_attributes']:

        # If the attribute is in stored_attributes it was updated by the user, so it is already in the
        # json and can be ignored
        if int(attribute['attribute_id']) not in stored_attributes:
          attributes_json.append({'attribute_id': attribute['attribute_id'], 'type': attribute['type']})
  if not attribute_form_id:
    fail('no attribute form with the given id')
  print('Updating attribute form: ', str(attribute_form_name), '... ', sep = '', end = '')

  # Post an attribute form
  data = api_mosaic.put_attribute_form(attribute_form_id, name = name, attributes = attributes_json)
  print('complete')

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

  # Required arguments
  parser.add_argument('--attribute_form_id', '-i', required = True, metavar = 'string', help = 'The id of the attribute form to update')

  # Optional arguments
  parser.add_argument('--name', '-n', required = False, metavar = 'string', help = 'The name of the attribute form')
  parser.add_argument('--required_attributes', '-r', required = False, metavar = 'string', help = 'A comma separated list of the ids of all required attributes')
  parser.add_argument('--suggested_attributes', '-s', required = False, metavar = 'string', help = 'A comma separated list of the ids of all suggested attributes')
  parser.add_argument('--optional_attributes', '-o', required = False, metavar = 'string', help = 'A comma separated list of the ids of all optional attributes')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
