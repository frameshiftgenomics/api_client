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
  from mosaic import Mosaic, Project, Store
  api_store = Store(config_file = args.client_config)
  api_mosaic = Mosaic(config_file = args.client_config)

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # Get the project settings
  for attribute in project.get_project_attributes():
    if not args.verbose: 
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
      print('    is_public: ', attribute['is_public'], sep = '')
      if attribute['predefined_values']:
        print('    predefined_values:')
        for value in attribute['predefined_values']:
          print('      ', value, sep = '')
      if attribute['source']:
        print('    source: ', attribute['source'], sep = '')
      if attribute['start_attribute_id']:
        print('    Start id: ', attribute['start_attribute_id'], ', End id: ', attribute['end_attribute_id'], sep = '')
      print('    created_at: ', attribute['created_at'], ', updated_at: ', attribute['updated_at'], sep = '')
      if args.include_values:
        print('    Values:')
        for value in attribute['values']:
          print('      ', value['value'], ': ', value['project_id'])

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # Include values
  parser.add_argument('--include_values', '-i', required = False, action = 'store_true', help = 'Include attribute values in the output. Only output when used in conjunction with --verbose')

  # Verbose output
  parser.add_argument('--verbose', '-v', required = False, action = 'store_true', help = 'Provide a verbose output')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print(message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
