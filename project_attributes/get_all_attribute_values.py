import argparse
import os
import sys

from pprint import pprint
from sys import path

def main():

#  # Add the parent directory of the script to sys.path and import modules
#  parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#  sys.path.append(parent_dir)
#  import general_modules
#  general_modules.initialise_script()

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
  import general_modules
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

  # Find the attribute
  values = []
  for attribute in project.get_project_attributes():
    if attribute['id'] == int(args.attribute_id):
      predefined_values = attribute['predefined_values']

      # Loop over all of the values and find all unique values
      for value_info in attribute['values']:
        if value_info['value'] not in values and value_info['value']:

          # If the display_non_predefined flag is set, only store the value if it is not
          # a predefined value
          if value_info['value'] not in predefined_values or not args.display_non_predefined:
            values.append(value_info['value']) 
  for value in sorted(values):
    print('\'', value, '\'', sep = '')

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
  project_arguments.add_argument('--attribute_id', '-i', required = True, metavar = 'integer', help = 'The attribute id to view')

  # Verbose output
  display_arguments.add_argument('--display_non_predefined', '-dn', required = False, action = 'store_true', help = 'Only display values that are not in the predefined values list')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
