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
  try:
    project = api_mosaic.get_project(args.project_id)
  except Exception as e:
    fail('Unable to open project with the given id. The project id must be a valid integer')

  # Check for mututally exclusive options
  if args.default and args.latest:
    fail('cannot request the of the default and latest annotations simultaneously')

  # Get the annotation version information
  for annotation_version in project.get_variant_annotation_versions(args.annotation_id):
    if args.default:
      if annotation_version['version'] == 'default':
        if args.ids_only:
          print(annotation_version['id'])
        else:
          print(annotation_version['version'], ': ', annotation_version['id'], ', redirects to: ', annotation_version['redirect_to_id'], sep = '')
    elif args.latest:
      if annotation_version['version'] == 'Latest':
        if args.ids_only:
          print(annotation_version['id'])
        else:
          print(annotation_version['version'], ': ', annotation_version['id'], ', redirects to: ', annotation_version['redirect_to_id'], sep = '')
    else:
      if annotation_version['version'] == 'default' or annotation_version['version'] == 'Latest':
        if args.ids_only:
          print(annotation_version['id'])
        else:
          print(annotation_version['version'], ': ', annotation_version['id'], ', redirects to: ', annotation_version['redirect_to_id'], sep = '')
      else:
        if args.ids_only:
          print(annotation_version['id'])
        else:
          print(annotation_version['version'], ': ', annotation_version['id'], sep = '')

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
  required_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to get annotations for')

  # Get the annotation id
  required_arguments.add_argument('--annotation_id', '-i', required = True, metavar = 'integer', help = 'The annotation id to get')

  # Optional arguments
  optional_arguments.add_argument('--default', '-d', required = False, action = 'store_true', help = 'Get the id of the default version')
  optional_arguments.add_argument('--latest', '-l', required = False, action = 'store_true', help = 'Get the id of the latest version')

  # Display arguments
  optional_arguments.add_argument('--ids_only', '-io', required = False, action = 'store_true', help = 'Only output the annotation id')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
