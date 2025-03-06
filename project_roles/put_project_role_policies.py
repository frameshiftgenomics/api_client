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
  from mosaic import Mosaic, Project, Store
  api_store = Store(config_file = args.client_config)
  api_mosaic = Mosaic(config_file = args.client_config)

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # Get the role_id for the user
  role_id = False
  for user in project.get_roles()['data']:
    if int(user['user_id']) == int(args.user_id):
      role_id = user['id']
      role_type_id = user['role_type_id']

  # If the user wasn't found, fail
  if not role_id:
    fail('did not find user with id ' + str(args.user_id) + ' in this project')

  # Update the role for this project
  policy_ids = args.policy_ids.split(',') if ',' in args.policy_ids else [args.policy_ids]
  project.put_project_role(role_id, role_type_id, user_id = args.user_id, policy_ids = policy_ids)

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # User ids
  parser.add_argument('--user_id', '-u', required = True, metavar = 'integer', help = 'The user id to assign the policy to')

  # Policy ids
  parser.add_argument('--policy_ids', '-o', required = True, metavar = 'string', help = 'A comma separated list of policy ids to assign to this user')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
