import argparse
import datetime
import os

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

  # Get the data groups in the project
  has_attribute = False
  for data_group in project.get_project_data_group_attributes():
    if int(data_group['id']) == int(args.attribute_id):
      has_attribute = True

      # Get the ids of all the attributes in the data group
      data_group_attributes = {}
      for attribute in data_group['data_group_attributes']:
        data_group_attributes[str(attribute['attribute_id'])] = {'id': str(attribute['id'])}
      break
  if not has_attribute:
    fail('Data group with id ' + str(args.attribute_id) + ' is not in this project, so an instance cannot be added')

  # Check the format of the record date and set to today if none is give
  args.record_date = str(datetime.now()).split(' ')[0] if not args.record_date else args.record_date
  try:
    datetime.strptime(args.record_date, '%Y-%m-%d')
  except ValueError:
    fail('Incorrect format for date (YYYY-MM-DD)')

  # Check that all the attribute ids are in the data group
  attribute_array = []
  for attribute_info in args.attributes.split(','):
    if ':' not in attribute_info:
      fail('Format of attribute information is incorrect. The required format is ID:value,ID:value, etc. Please check the entered string')
    attribute_id = attribute_info.split(':')[0]
    attribute_value = attribute_info.split(':')[1]
    if str(attribute_id) not in data_group_attributes:
      fail('Attribute with id ' + str(attribute_id) + ' is not in the given data group. Please check the entered values')
    attribute_array.append({'attribute_id': int(attribute_id), 'value': attribute_value, 'record_date': str(args.record_date)})

  # Post the data group instance
  try:
    project.post_data_group_instance(args.attribute_id, record_date = args.record_date, data_group_attributes = attribute_array)
  except Exception as e:
    fail('Failed to create data group instance with the following error' + str(e))

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

  # The project and attribute ids
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')
  project_arguments.add_argument('--attribute_id', '-i', required = True, metavar = 'integer', help = 'The id of the data group')

  # Required parameters
  required_arguments.add_argument('--attributes', '-t', required = True, metavar = 'string', help = 'A comma separated list of attributes to add in the format ID:value. Example: 1:value1,2:value2')

  # Optional arguments
  optional_arguments.add_argument('--record_date', '-r', required = False, metavar = 'string', help = 'The record date to add in the format YYYY-MM-DD')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
