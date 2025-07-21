import argparse
import os

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

  # Get information about the data group
  has_attribute = False
  for attribute in project.get_project_data_group_attributes():
    if int(attribute['id']) == int(args.attribute_id):
      has_attribute = True
      break

  # Check the optional attributes
  name = args.name if args.name else None
  description = args.description if args.description else None

  # If the is_editable, or not editable options are set
  if args.is_editable and args.is_not_editable:
    fail('The is_editable and is_not_editable flags cannot be set simultaneously')
  elif args.is_editable:
    is_editable = 'true'
  elif args.is_not_editable:
    is_editable = 'false'
  else:
    is_editable = None

  # If this a private attribute and the is_public flag is set, make the data group public
  is_public = None
  if not attribute['is_public'] and args.is_public:
    is_public = 'true'

  # Edit the data group attribute
  project.put_project_data_group_attribute(args.attribute_id, name = name, description = description, is_public = is_public, is_editable = is_editable)

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
  project_arguments.add_argument('--attribute_id', '-i', required = True, metavar = 'integer', help = 'The Mosaic project data attribute id to edit')

  # Optional parameters
  optional_arguments.add_argument('--name', '-n', required = False, metavar = 'string', help = 'The name of the data group attribute')
  optional_arguments.add_argument('--description', '-d', required = False, metavar = 'string', help = 'The description of the data group attribute')
  optional_arguments.add_argument('--is_public', '-u', required = False, action = 'store_true', help = 'Set to make the data group attribute public')
  optional_arguments.add_argument('--is_editable', '-e', required = False, action = 'store_true', help = 'Set to make the data group attribute editable')
  optional_arguments.add_argument('--is_not_editable', '-ne', required = False, action = 'store_true', help = 'Set to make the data group attribute NOT editable')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
