import argparse
import os
import time

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

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # Get all attributes in the project. When looping over data group attributes, this is needed to get the names
  # of the data group attributes
  project_attributes = {}
  for attribute in project.get_project_attributes():
    project_attributes[attribute['id']] = attribute['name']

  # Get all data group attributes
  for data_group_instance in project.get_data_group_instances(args.attribute_id):
    print('instance id: ', data_group_instance['id'], sep = '')

    # Format the time stringds
    format_string = "%Y-%m-%dT%H:%M:%S.%fZ"
    record_date = str(datetime.strptime(data_group_instance['record_date'], format_string)).split('.')[0]
    created_at = str(datetime.strptime(data_group_instance['created_at'], format_string)).split('.')[0]
    updated_at = str(datetime.strptime(data_group_instance['updated_at'], format_string)).split('.')[0]
    if args.display_all_information:
      print('  record date: ', record_date, sep = '')
      print('  created_at: ', created_at, ', updated_at: ', updated_at, sep = '')
    for attribute in data_group_instance['data_group_attribute_values']:
      if args.display_all_information:
        print('  attribute id: ', attribute['attribute_id'], ', id: ', attribute['id'], sep = '')
        format_string = '%Y-%m-%dT%H:%M:%S'
        record_date = str(attribute['record_date']).split('+')[0]
        record_date = str(datetime.strptime(record_date, format_string)).split('.')[0]
        print('    record_date: ', record_date, sep = '')
        print('    custom_display_format: ', attribute['custom_display_format'], sep = '')
        print('    display_type: ', attribute['display_type'], sep = '')
        print('    value_type: ', attribute['value_type'], sep = '')
        print('    value: ', attribute['value'], sep = '')
      else:
        print('  attribute id: ', attribute['attribute_id'], ', id: ', attribute['id'], ', value: ', attribute['value'], sep = '')

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
  project_arguments.add_argument('--attribute_id', '-i', required = True, metavar = 'integer', help = 'The Mosaic id of the data group attribute')

  # Optional viewing options
  display_arguments.add_argument('--display_all_information', '-da', required = False, action = 'store_true', help = 'Include all data group information')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
