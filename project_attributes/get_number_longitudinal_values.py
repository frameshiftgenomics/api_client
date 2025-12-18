import argparse
import os
import sys

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
  project_value_counts = {}
  for attribute in project.get_project_attributes():
    if attribute['id'] == int(args.attribute_id):

      # Loop over all of the values and find all unique values
      for value_info in attribute['values']:
        if value_info['project_id'] not in project_value_counts:
          project_value_counts[value_info['project_id']] = 1
        else:
          project_value_counts[value_info['project_id']] += 1

  # Write out the results
  output_list = []
  for project_id in sorted(project_value_counts):
    number_values = project_value_counts[project_id]
    if number_values > 1 or not args.display_multivalued:
      if args.output_comma_separated_list:
        output_list.append(str(project_id))
      else:
        print(project_id, ':\t', project_value_counts[project_id], sep = '')

  # Output the comma separated list
  if args.output_comma_separated_list and len(output_list) > 0:
    print(','.join(output_list))

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

  # Only display projects with multiple values
  display_arguments.add_argument('--display_multivalued', '-dm', required = False, action = 'store_true', help = 'Only show projects with multiple values for the attribute')
  display_arguments.add_argument('--output_comma_separated_list', '-ol', required = False, action = 'store_true', help = 'Output a comma separated list of project ids')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
