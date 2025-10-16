import os
import argparse

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

  # Get the array of ids to look at
  attribute_ids = False
  if args.attribute_ids:
    attribute_ids = args.attribute_ids.split(',') if ',' in args.attribute_ids else [args.attribute_ids]

  # Get the project settings
  for attribute in project.get_project_attributes():
    display = False if args.attribute_ids else True
    if args.attribute_ids:
      if str(attribute['id']) in attribute_ids:
        display = True

    # Only display if the attribute is requested
    if display:
      if not args.display_all_information:
        print(attribute['name'], ': ', attribute['id'], sep = '')
      else:
        print(attribute['name'], ' (id: ', attribute['id'], ')', sep = '')
        if attribute['description']:
          print('  description: ', attribute['description'], sep = '')
        print('    uid: ', attribute['uid'], sep = '')
        print('    value_type: ', attribute['value_type'], sep = '')
        print('    original_project_id: ', attribute['original_project_id'], sep = '')
        print('    is_custom: ', attribute['is_custom'], sep = '')
        print('    is_editable: ', attribute['is_editable'], sep = '')
        print('    is_longitudinal: ', attribute['is_longitudinal'], sep = '')
        print('    is_public: ', attribute['is_public'], sep = '')
        print('    custom_display_format: ', attribute['custom_display_format'], sep = '')
        print('    display_type: ', attribute['display_type'], sep = '')
        if attribute['predefined_values']:
          print('    predefined_values:')
          for value in attribute['predefined_values']:
            print('      ', value, sep = '')
        else:
          print('    predefined values: none set')
        if attribute['source']:
          print('    source: ', attribute['source'], sep = '')
        if attribute['start_attribute_id']:
          print('    Start id: ', attribute['start_attribute_id'], ', End id: ', attribute['end_attribute_id'], sep = '')
        print('    created_at: ', attribute['created_at'], ', updated_at: ', attribute['updated_at'], sep = '')
        if args.include_values:
          print('    Values:')
          for value in attribute['values']:
            print('      ', value['value'], ': ', value['id'])
        print('    policies: ', attribute['policies'], sep = '')

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
  project_arguments.add_argument('--attribute_ids', '-i', required = False, metavar = 'string', help = 'A comma separated list of attribute ids to view. If omitted, all will be shown')

  # Include values
  display_arguments.add_argument('--include_values', '-v', required = False, action = 'store_true', help = 'Include attribute values in the output. Only output when used in conjunction with --verbose')

  # Verbose output
  display_arguments.add_argument('--display_all_information', '-da', required = False, action = 'store_true', help = 'Display Provide a verbose output')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
