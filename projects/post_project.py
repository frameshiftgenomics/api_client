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

  # Check that the reference is valid
  allowed_references = ['GRCh37', 'GRCh38']
  if args.reference not in allowed_references:
    fail('unknown reference')

  # Check the privacy level is allowed
  allowed_privacy = ['public', 'protected', 'private']
  args.privacy_level = 'private' if not args.privacy_level else args.privacy_level
  if args.privacy_level not in allowed_privacy:
    fail('unknown privacy level')
  
  # If collection_projects is set, make sure the is_collection is also set
  collection_projects = None
  if args.collection_projects:
    if not args.is_collection:
      fail('A list of project ids to add to the collection is provided. To create a collection, the --is_collection (-co) must be set')
    collection_projects = args.collection_projects.split(',') if ',' in args.collection_projects else [args.collection_projects]

  # Create a project
  project = api_mosaic.post_project(args.name, \
                                    args.reference, \
                                    nickname = args.nickname, \
                                    description = args.description, \
                                    is_collection = args.is_collection, \
                                    collection_projects = collection_projects, \
                                    privacy_level = args.privacy_level, \
                                    template_project_id = args.template_project_id)

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

  # The project information
  required_arguments.add_argument('--name', '-n', required = True, metavar = 'string', help = 'The project name')
  required_arguments.add_argument('--reference', '-r', required = True, metavar = 'string', help = 'The project reference')
  optional_arguments.add_argument('--nickname', '-m', required = False, metavar = 'string', help = 'The project nickname')
  optional_arguments.add_argument('--description', '-d', required = False, metavar = 'string', help = 'The project description')
  optional_arguments.add_argument('--privacy_level', '-l', required = False, metavar = 'string', help = 'The projects privacy level. Default: private')

  # Information for creating a collection
  optional_arguments.add_argument('--is_collection', '-co', required = False, action = 'store_true', help = 'Set if this is to be a collection, not a project')
  optional_arguments.add_argument('--collection_projects', '-cp', required = False, metavar = 'string', help = 'If is_collection is set, a list of project ids to add to the collection can be set')

  # Set the project template
  optional_arguments.add_argument('--template_project_id', '-t', required = False, metavar = 'integer', help = 'Supply the id of a template project to apply this template on creation')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
