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

  # Check that the task type id is valid
  if int(args.task_type_id) > 4:
    fail('The task type id supplied is not valid. Please select an integer between 1 and 4')

  # Open an api client project object for the defined project
  try:
    project = api_mosaic.get_project(args.project_id)
  except Exception as e:
    fail('Failed to open requested project. Error was: ' + str(e))

  # Check if this is a collection
  is_collection = False
  if project.get_project()['is_collection']:
    is_collection = True

  # The cascade option is only available for collections
  if args.cascade and not is_collection:
    fail('The flag to cascade is set, but the supplied project id is not for a collection')

  # Set the array of attribute ids
  attribute_ids = None
  if args.attribute_ids:
    attribute_ids = args.attribute_ids.split(',') if args.attribute_ids else [args.attribute_ids]

  # Apply the attributes
  try:
    project.put_task_type_attributes(args.task_type_id, attribute_ids = attribute_ids, cascade_update = args.cascade)
  except Exception as e:
    fail('Failed to apply task type attributes. Error was: ' + str(e))

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

  # The task type to apply the attributes to
  project_arguments.add_argument('--task_type_id', '-t', required = True, metavar = 'integer', help = 'The id of the task type (e.g. 4: Primary ClinVar Review). Tasks created for this type will include the supplied attributes in the Tasks view')

  # A list of attribute ids to add to the tasks
  required_arguments.add_argument('--attribute_ids', '-i', required = True, metavar = 'string', help = 'A comma separated list of attribute ids to add to the task types')

  # A list of attribute ids to add to the tasks
  optional_arguments.add_argument('--cascade', '-ca', required = False, action = 'store_true', help = 'If set, the attributes will be cascaded to all sub-projects')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
