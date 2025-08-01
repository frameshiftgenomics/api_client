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

  # The -dn and -dr options are mutually exclusive
  if args.display_all and args.display_user_id_and_type_id:
    fail('The -dn and -dr options are mutually exclusive')

  # If using a verbose output, get the role types
  if args.display_all:
    role_type_ids = {}
    for role_type in api_mosaic.get_role_types():
      role_type_ids[role_type['id']] = role_type['display_name']

  # Get the roles
  for user in project.get_roles():
    if args.display_all:
      print('Role id: ', user['id'], sep = '')
      print('  user_id: ', user['user_id'], sep = '')
      print('  can_download: ', user['can_download'], sep = '')
      print('  can_launch_app: ', user['can_launch_app'], sep = '')
      print('  role_type: ', role_type_ids[user['role_type_id']], ' (id: ', user['role_type_id'], ')', sep = '')
    elif args.display_user_id_and_type_id:
      print(user['user_id'], user['role_type_id'], sep = '\t')
    else:
      print(user['user_id'])

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

  # Verbose output
  display_arguments.add_argument('--display_all', '-da', required = False, action = 'store_true', help = 'If set, details of the role will be provided')
  display_arguments.add_argument('--display_user_id_and_type_id', '-dr', required = False, action = 'store_true', help = 'If set, details of the role will be provided')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
