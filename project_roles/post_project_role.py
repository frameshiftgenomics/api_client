import argparse
import json
import os

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

  # Get the project
  try:
    project = api_mosaic.get_project(args.project_id)
  except Exception as e:
    fail('Couldn\'t open project. Error was: ' + str(e))

  # Update the project roles
  project.post_project_role(args.user_id, args.role_type_id, can_download=None, can_launch_app=None, policy_ids=None, disable_notification = args.disable_notification)

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

  # Required arguments
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'string', help = 'The id of the Mosaic project')
  project_arguments.add_argument('--user_id', '-u', required = True, metavar = 'string', help = 'The role id of the user to update')
  project_arguments.add_argument('--role_type_id', '-r', required = True, metavar = 'string', help = 'The id role to update the user to. 2: Owner, 3: Admin, 4: Member, 5: Viewer, 6: Technical Staff')

  # Optional arguments
  project_arguments.add_argument('--disable_notification', '-dn', required = False, action = 'store_true', help = 'Do not send a notification when the role is added')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
