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

  # Create the project object
  project = api_mosaic.get_project(args.project_id)

  # Check the resource type to be deleted is valid
  allowed_types = ['project_attribute',
                   'project_conversation']
  resource_type = args.resource_type if args.resource_type in allowed_types else fail('Unknown resource type') 

  # Delete the policy resource
  project.delete_policy_resource(args.policy_id, resource_type):

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

  # The project id 
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id')

  # The policy id to post attributes to
  parser.add_argument('--policy_id', '-i', required = True, metavar = 'integer', help = 'The policy id to post attributes to')

  # The type or resource to delete and the id of the resource
  parser.add_argument('--resource_type', '-t', required = True, metavar = 'string', help = 'The resource type to dekete: project_attribute, project_conversation')
  parser.add_argument('--resource_id', '-r', required = True, metavar = 'integer', help = 'The id of the resource to delete')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
