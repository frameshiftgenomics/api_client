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

  # If the attributes in the data group are to be updated
  # Generate a list of attribute ids
  if args.attribute_ids:
    attribute_ids = [int(attribute_id) for attribute_id in args.attribute_ids.split(',')] if ',' in args.attribute_ids else [int(args.attribute_ids)]
  else:
    attribute_ids = []

  # Check that all the attributes are in the project and are longitudinal
  project_attributes = {}
  attribute_array = []
  for project_attribute in project.get_project_attributes():
    project_attributes[str(project_attribute['id'])] = project_attribute['is_longitudinal']
  for attribute_id in attribute_ids:
    if str(attribute_id) not in project_attributes:
      fail('Attribute id ' + str(attribute_id) + ' is not in the project and so cannot be added to the data group')
    if not project_attributes[str(attribute_id)]:
      fail('Attribute id ' + str(attribute_id) + ' is not a longitudinal attribute and so cannot be added to the data group')
    attribute_array.append({"attribute_id": int(attribute_id)})

  # If the annotations in the data group are to be updated
  # Generate a list of annotation ids
  if args.annotation_version_ids:
    annotation_version_ids = [int(annotation_id) for annotation_id in args.annotation_version_ids.split(',')] if ',' in args.annotation_version_ids else [int(args.annotation_version_ids)]
  else:
    annotation_version_ids = []

  # Check that all the annotation version ids exist in the project
  project_annotations = []
  annotation_array = []
  for project_annotation in project.get_variant_annotations():
    project_annotations.extend([int(version['id']) for version in project_annotation['annotation_versions']])
  for annotation_version_id in annotation_version_ids:
    if annotation_version_id not in project_annotations:
      fail('Annotation version id ' + str(annotation_version_id) + ' is not in the project and so cannot be added to the data group')
    annotation_array.append({"annotation_version_id": int(annotation_version_id)})

  # Edit the data group attribute
  try:
    project.put_project_data_group_attribute(args.attribute_id, name = name, description = description, is_public = is_public, is_editable = is_editable, data_group_attributes = attribute_array, data_group_annotation_versions = annotation_array)
  except Exception as e:
    fail('Failed to update data group. Error was: ' + str(e))

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

  # Add attributes and / or annotations
  optional_arguments.add_argument('--attribute_ids', '-ai', required = False, metavar = 'string', help = 'A comma separated list of attribute ids to include in the data group. This must be a complete list. Any exsiting attributes in the data group will be removed if they are not included in this list')
  optional_arguments.add_argument('--annotation_version_ids', '-ni', required = False, metavar = 'string', help = 'A comma separated list of annotation ids to include in the data group. This must be a complete list. Any exsiting annotations in the data group will be removed if they are not included in this list')

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
