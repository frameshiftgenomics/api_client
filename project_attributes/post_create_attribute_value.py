import os
import argparse

from datetime import datetime
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

  # If a record date isn't provided, use todays date
  args.record_date = str(datetime.now()).split(' ')[0] if not args.record_date else args.record_date 

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # Check that the attribute is longitudinal
  has_attribute = False
  for attribute in project.get_project_attributes():
    if int(attribute['id']) == int(args.attribute_id):
      if not attribute['is_longitudinal']:
        fail('Attribute is not longitudinal. This route is only for longitudinal attributes')
      has_attribute = True

      # Get the last value associated with the attribute. If there is only one value and this is None, there
      # are no values (just a null value) and so the null can be replaced, rather than creating a new value
      last_value = attribute['values'][-1]['value']
      if not last_value and len(attribute['values']) == 1:
        value_id = attribute['values'][0]['id']
        replace_null_value(project, args.attribute_id, value_id, args.value, args.record_date)
      else:
        add_new_value(project, args.attribute_id, args.value, args.record_date)

  # If the attribute was not found in the project, fail
  if not has_attribute:
    fail('Attribute is not present in the project')

# Replace the existing null value with the actual value
def replace_null_value(project, attribute_id, value_id, value, record_date):
  try:
    project.put_update_attribute_value(attribute_id, value_id, value = value, record_date = record_date)
  except Exception as e:
    fail('Failed to create attribute value (replaceing null). Error is: ' + str(e))

# Add a new value to the longitudinal attribute
def add_new_value(project, attribute_id, value, record_date):
  try:
    project.post_create_attribute_value(attribute_id, value = value, record_date = record_date)
  except Exception as e:
    fail('Failed to create attribute value. Error is: ' + str(e))

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

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')
  project_arguments.add_argument('--attribute_id', '-i', required = True, metavar = 'integer', help = 'The Mosaic attribute id to add a value to')

  # Required arguments to update
  required_arguments.add_argument('--value', '-v', required = True, metavar = 'string', help = 'The value of the attribute')

  # Optional arguments to update
  required_arguments.add_argument('--record_date', '-r', required = False, metavar = 'string', help = 'The record date for the attribute')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
