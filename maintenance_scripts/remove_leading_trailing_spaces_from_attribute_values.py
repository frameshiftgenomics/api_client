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
  try:
    project = api_mosaic.get_project(args.project_id)
  except Exception as e:
    fail('Failed to open project. Error was: ' + str(e))

  # Check the format of the record date and set to today if none is give
  record_date = str(datetime.now()).split(' ')[0]
  try:
    datetime.strptime(record_date, '%Y-%m-%d')
  except ValueError:
    fail('Incorrect format for date (YYYY-MM-DD)')

  # Get the attribute values
  attribute_ids = [int(x) for x in args.attribute_ids.split(',')]
  for attribute in project.get_project_attributes():
    if attribute['id'] in attribute_ids:
      value_list = []
      print('Attribute: ', attribute['id'])
      for value_info in attribute['values']:
        value = value_info['value']
        project_id = value_info['project_id']
        if value:

          # If the value starts or ends with a space, remove it and store the updated value
          if value.startswith(' ') or value.endswith(' '):
            new_value = value.strip(' ').rstrip(' ')
            value_id = value_info['id']

            # Open the project and update the value
            try:
              new_project = api_mosaic.get_project(project_id)
              try:
                new_project.put_update_attribute_value(attribute['id'], value_id, value = new_value, record_date = record_date)
              except Exception as e:
                warning('unable to update value for project: ' + str(project_id))
            except Exception as e:
              warning('unable to open project: ' + str(project_id))
            if new_value not in value_list:
              value_list.append(new_value)

          # If the value does not start or end with a space, store the value
          else:
            if value not in value_list:
              value_list.append(value)

      # Print out the list of unique values
      print('  These are the unique values for this attribute:')
      sorted_list = sorted(value_list)
      for value in sorted_list:
        print('    ', value, sep = '')

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
  project_arguments.add_argument('--attribute_ids', '-i', required = True, metavar = 'string', help = 'A comma separated list of attribute ids to update')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

def warning(message):
  print('WARNING: ', message, sep = '')

if __name__ == "__main__":
  main()
