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

  # Get any attribute_ids or conversation_ids
  attribute_id = args.attribute_id if args.attribute_id else None
  conversation_id = args.conversation_id if args.conversation_id else None
  if not attribute_id and not conversation_id:
    fail('An attribute or conversation id must be provided')

  # Post the attribute to the policy
  project.post_policy_project_resource(args.policy_id, attribute_id = attribute_id, conversation_id = conversation_id)

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
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id')

  # The policy id to post attributes to
  required_arguments.add_argument('--policy_id', '-i', required = True, metavar = 'integer', help = 'The policy id to post attributes to')

  # The attribute id to post to the policy
  optional_arguments.add_argument('--attribute_id', '-t', required = False, metavar = 'integer', help = 'The attribute id to post to the policy')
  optional_arguments.add_argument('--conversation_id', '-v', required = False, metavar = 'integer', help = 'The conversation id to post to the policy')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
