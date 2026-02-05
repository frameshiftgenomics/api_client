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

  # Get the project settings
  is_editable = 'false' if args.is_editable else 'true'
  if args.is_public == 'public':
    is_public = 'true'
  elif args.is_public == 'private':
    is_public = 'false'
  else: 
    fail('is_public must be "public" or "private"')

  # Check the attribute type
  if args.value_type != 'float' and args.value_type != 'string' and args.value_type != 'timestamp':
    fail('value_type must be "float" or "string", or "timestamp"')

  # Set the predefined values
  predefined_values = args.predefined_values.split(',') if args.predefined_values else None

  # Deal with whether the attribute is editable or longitudinal
  is_editable = 'false' if args.is_editable else 'true'
  is_longitudinal = 'true' if args.is_longitudinal else 'false'
  only_suggest_predefined = 'true' if args.only_suggest_predefined else 'false'

  # Create the attribute
  try:
    project.post_project_attribute(description = args.description, \
                                   name = args.name, \
                                   predefined_values = predefined_values, \
                                   value = args.value, \
                                   value_type = args.value_type, \
                                   is_editable = is_editable, \
                                   is_longitudinal = is_longitudinal, \
                                   is_public = is_public, \
                                   only_suggest_predefined_values = only_suggest_predefined)
  except Exception as e:
    fail('Failed to create attribute. Error was: ' + str(e))

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

  # Required arguments for creating a new attribute
  required_arguments.add_argument('--name', '-n', required = True, metavar = 'string', help = 'The name of the attribute')
  required_arguments.add_argument('--is_public', '-u', required = True, metavar = 'string', help = 'Is the project "public" or "private"')
  required_arguments.add_argument('--value_type', '-t', required = True, metavar = 'string', help = 'The value type must be "float", "string", or "timestamp"')

  # Optional arguments to update
  optional_arguments.add_argument('--description', '-d', required = False, metavar = 'string', help = 'The attribute description')
  optional_arguments.add_argument('--is_editable', '-e', required = False, action = 'store_true', help = 'If set, the attribute will not be editable')
  optional_arguments.add_argument('--is_longitudinal', '-l', required = False, action = 'store_true', help = 'If set, the attribute will not longitudinal')
  optional_arguments.add_argument('--only_suggest_predefined', '-o', required = False, action = 'store_true', help = 'If set, when editing the attribute, only predefined values will be suggested')
  optional_arguments.add_argument('--predefined_values', '-r', required = False, metavar = 'string', help = 'A comma separated list of values that will be available by default')
  optional_arguments.add_argument('--value', '-v', required = False, metavar = 'string', help = 'The value of the attribute')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
