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

  # Check that the start and end attribute ids correspond to timestamp attributes that exist in this project
  existing_attributes = {}
  for attribute in project.get_project_attributes():
    existing_attributes[int(attribute['id'])] = {'name': attribute['name'], 'value_type': attribute['value_type'], 'is_public': attribute['is_public']}

  # Check the start id is an existing timestamp
  if int(args.start_attribute_id) not in existing_attributes:
    fail('Start attribute (id: ' + str(args.start_attribute_id) + ') is not available in this project')
  else:
    if existing_attributes[int(args.start_attribute_id)]['value_type'] != 'timestamp':
      fail('Start attribute (id: ' + str(args.start_attribute_id) + ') is not a timestamp')

  # Check the end id is an existing timestamp
  if int(args.end_attribute_id) not in existing_attributes:
    fail('End attribute (id: ' + str(args.end_attribute_id) + ') is not available in this project')
  else:
    if existing_attributes[int(args.end_attribute_id)]['value_type'] != 'timestamp':
      fail('End attribute (id: ' + str(args.end_attribute_id) + ') is not a timestamp')

  # If the interval is to be public, make sure the end dates are public
  is_public = 'false'
  if args.is_public:
    is_public = 'true'
    is_start_public = existing_attributes[int(args.start_attribute_id)]['is_public']
    is_end_public = existing_attributes[int(args.end_attribute_id)]['is_public']
    if not is_start_public or not is_end_public:
      fail('both the start and end timestamps must be public to create a public interval')

  # Set the policy ids
  policy_ids = None
  if args.policy_ids:
    policy_ids = args.policy_ids.split(',') if ',' in args.policy_ids else [args.policy_ids]

  # Create the interval
  description = args.description if args.description else None
  project.post_project_interval_attribute(args.name, args.start_attribute_id, args.end_attribute_id, description=description, is_public=is_public, policy_ids=policy_ids)

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # Required information about the interval
  parser.add_argument('--name', '-n', required = True, metavar = 'string', help = 'The name of the project interval attribute')
  parser.add_argument('--start_attribute_id', '-s', required = True, metavar = 'integer', help = 'The id of the start timestamp attribute')
  parser.add_argument('--end_attribute_id', '-e', required = True, metavar = 'integer', help = 'The id of the end timestamp attribute')

  # Optional information about the interval
  parser.add_argument('--description', '-d', required = False, metavar = 'string', help = 'An optional description of the project interval attribute')
  parser.add_argument('--is_public', '-u', required = False, action = 'store_true', help = 'By default, the created interval will be provate. Set this flag to make it public.')
  parser.add_argument('--policy_ids', '-o', required = False, metavar = 'string', help = 'A comma separated list of policy ids to assign to this user')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
