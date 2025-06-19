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

  # Get the existing conversation group
  for group in api_mosaic.get_conversation_groups():
    if int(group['id']) == int(args.group_id):
      existing_name = group['name']
      existing_description = group['description']
      existing_user_ids = group['user_ids']
      break

  # Create a new conversation group
  name = args.name if args.name else existing_name
  description = args.description if args.description else existing_description
  if args.user_ids:
    user_ids = args.user_ids.split(',') if ',' in args.user_ids else [args.user_ids]
  else:
    user_ids = existing_user_ids

  # Update the conversation group
  try:
    data = api_mosaic.put_conversation_groups(args.group_id, name = name, description = description, user_ids = user_ids)
  except Exception as e:
    fail('Failed to update the conversation group. Error: ' + str(e))

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

  # The id of the conversation group
  required_arguments.add_argument('--group_id', '-i', required = True, metavar = 'integer', help = 'The id of the conversation group')

  # Get information on the conversation group
  optional_arguments.add_argument('--name', '-n', required = False, metavar = 'string', help = 'The name of the conversation group')
  optional_arguments.add_argument('--user_ids', '-u', required = False, metavar = 'string', help = 'A comma separated list of user ids to add to the conversation group')
  optional_arguments.add_argument('--description', '-d', required = False, metavar = 'string', help = 'A description of the conversation group')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
