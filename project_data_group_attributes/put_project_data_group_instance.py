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
  if not has_attribute:
    fail('The attribute with id ' + str(args.attribute_id) + ' is not in this project, so a record for it cannot be edited')

  # Check that a record with the given id exists for this data group
  has_instance = False
  for instance in project.get_data_group_instances(args.attribute_id):
    if int(instance['id']) == int(args.instance_id):
      has_instance = True
      break
  if not has_instance:
    fail('No instance with the given id exists for the requested data group attribute')

  # Update the variants in the project
  if args.variant_ids:
    variant_ids = [int(variant_id) for variant_id in args.variant_ids.split(',')]
  else:
    variant_ids = None
  for variant_id in variant_ids:
    try:
      variant_info = project.get_variant(variant_id)
      if not variant_info:
        fail('Failed to get variant with id ' + str(variant_id) + '. Check that this variant exists in this project')
    except Exception as e:
      fail('Failed to get variant with id ' + str(variant_id) + '. Check that this variant exists in this project')

  # Edit the data group attribute
  try:
    project.put_project_data_group_instance(args.attribute_id, args.instance_id, record_date=None, data_group_attribute_variant_ids = variant_ids)
  except Exception as e:
    fail('Failed to update instance. Error was: ' + str(e))

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
  project_arguments.add_argument('--attribute_id', '-i', required = True, metavar = 'integer', help = 'The id of the Mosaic project data group attribute to edit')
  project_arguments.add_argument('--instance_id', '-n', required = True, metavar = 'integer', help = 'The id of the Mosaic project data group instance to edit')

  # Optional parameters
  #optional_arguments.add_argument('--record_date', '-r', required = False, metavar = 'string', help = 'The date / time to set for this data group instance')
  optional_arguments.add_argument('--variant_ids', '-v', required = False, metavar = 'string', help = 'A comma separated list of variant ids to add to the instance')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
