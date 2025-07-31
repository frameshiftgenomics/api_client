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
    fail('Failed to open project with the given id. Error was: ' + str(e))

  # Check the inputted information
  allowed_types = ['float', 'string']
  if args.value_type not in allowed_types:
    fail('ERROR: the supplied value_type (' + str(args.value_type) + ') is invalid. Allowed values are: ' + ','.join(allowed_types))
  if args.privacy_level != 'public' and args.privacy_level != 'private':
    fail('ERROR: unknown privacy_level. Must be public or private')

  # Set the version name
  version_name = args.version_name if args.version_name else None

  # Check if an annotation of the same name exists in the project
  for annotation in project.get_variant_annotations():
    if str(annotation['name']) == str(args.name):
      if args.force_creation:
        print('Forced annotation creation. Annotation with the name "' + str(args.name) + '" already exists, but a new annotation was created with the same name')
      else:
        print('No annotation created. Annotation with the name "' + str(args.name) + '" already exists')
        exit(0)

  # Create the new annotation
  try:
    data = project.post_variant_annotation(name = args.name, \
                                           value_type = args.value_type, \
                                           privacy_level = args.privacy_level, \
                                           display_type = None, \
                                           severity = None, \
                                           category = args.category, \
                                           value_truncate_type = None, \
                                           value_max_length = None)
    annotation_id = data['id']

    # Get the id of the default version
    default_id = None
    for annotation_version in data['annotation_versions']:
      if annotation_version['version'] == 'default':
        default_id = annotation_version['id']
        break
  except Exception as e:
    fail('Failed to create annotation. Error was: ' + str(e))

  # If there is a version_name, create a new version
  if version_name:
    try:
      version_id = project.post_create_annotation_version(annotation_id, version_name)['id']
    except Exception as e:
      fail('Failed to create annotation version. Error was: ' + str(e))
  else:
    version_id = default_id

  # If the new annotation version is to be set as the latest, set it
  if args.set_as_latest:
    try:
      project.put_variant_annotation(annotation_id, latest_version_id = version_id)
    except Exception as e:
      fail('Failed to set new version as Latest. Error was: ' + str(e))

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
  required_arguments.add_argument('--name', '-n', required = True, metavar = 'string', help = 'The annotation name')
  required_arguments.add_argument('--category', '-t', required = True, metavar = 'string', help = 'The category to assign the annotation to')
  required_arguments.add_argument('--value_type', '-v', required = True, metavar = 'string', help = 'The annotation type: string or float')
  required_arguments.add_argument('--privacy_level', '-y', required = True, metavar = 'string', help = 'The annotation privacy: public or private')

  # Annotations will not be created if an annotation of the given name already exists. This
  # flag will force the annotation to be created even if an annotation of the same name exists
  optional_arguments.add_argument('--force_creation', '-f', required = False, action = 'store_true', help = 'Force annotation creation, even if an annotation of the same name exists')
  optional_arguments.add_argument('--version_name', '-vn', required = False, metavar = 'string', help = 'Optionally create an annotation version with this name')
  optional_arguments.add_argument('--set_as_latest', '-s', required = False, action = 'store_true', help = 'If --version_name is set, this flag will set the named version (or the default version if no name is given) as the latest')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
