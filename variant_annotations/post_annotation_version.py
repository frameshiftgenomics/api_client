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

  # Check that the annotation exists
  try:
    for annotation_version in project.get_variant_annotation_versions(args.annotation_id):

      # If the annotation already has a version with the same name, fail if there isn't a request to
      # overwrite
      if str(annotation_version['version']) == str(args.version_name):
        if not args.overwrite_version:
          fail('Annotation version with the name ' + str(args.version_name) + ' already exists. Set --overwrite_version (-o) to overwrite')
        else:

          # Delete the annotation version
          try:
            project.delete_variant_annotation_version(args.annotation_id, annotation_version['id'])
          except Exception as e:
            fail('Failed to delete existing annotation version. Error was: ' + str(e))
          break
  except Exception as e:
    fail('Could not get annotation. Check that this annotation exists in the specified project. Error was: ' + str(e))

  # Create the new annotation version
  try:
    project.post_create_annotation_version(args.annotation_id, args.version_name)
  except Exception as e:
    fail('Failed to add annotation. Error was: ' + str(e))

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

  # Information about the annotation being created
  required_arguments.add_argument('--annotation_id', '-i', required = True, metavar = 'integer', help = 'The id of the annotation to create a new version for')
  required_arguments.add_argument('--version_name', '-n', required = True, metavar = 'string', help = 'The name of the annotation version to create')

  # Optional arguments
  optional_arguments.add_argument('--overwrite_version', '-o', required = False, action = 'store_true', help = 'If set, existing annotation versions with the same name will be removed')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
