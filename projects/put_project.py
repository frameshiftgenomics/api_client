import argparse
import os
import time

from datetime import datetime
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
    fail('Failed to open project. Error was: ' + str(e))

  # Set the name, nickname and description
  name = args.name if args.name else None
  nickname = args.nickname if args.nickname else None
  description = args.description if args.description else None

  # If the primary_sample_id is given, check this sample is in the project
  primary_sample_id = None
  if args.primary_sample_id:
    has_sample_id = False
    for sample in project.get_samples():
      if int(sample['id']) == int(args.primary_sample_id):
        has_sample_id = True
        break
    if not has_sample_id:
      fail('supplied primary sample id is not the id of a sample in the project')
    else:
      primary_sample_id = args.primary_sample_id 

  # PUT the updates
  try:
    project.put_project(name = name, nickname = nickname, description = description, primary_sample_id = primary_sample_id)
  except Exception as e:
    fail('failed to PUT project updates. Error wes: ' + str(e))

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

  # The project id
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # Optional arguments
  optional_arguments.add_argument('--name', '-n', required = False, metavar = 'string', help = 'The name of the new data group view')
  optional_arguments.add_argument('--nickname', '-nn', required = False, metavar = 'string', help = 'The nickname of the new data group view')
  optional_arguments.add_argument('--description', '-d', required = False, metavar = 'string', help = 'A description of the new data group view')
  optional_arguments.add_argument('--primary_sample_id', '-s', required = False, metavar = 'integer', help = 'The id of the project sample to be designated as primary. Typically this is the id of the proband')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
