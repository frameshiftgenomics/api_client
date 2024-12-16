import os
import argparse

from pprint import pprint
from sys import path

def main():

  # Parse the command line
  args = parse_command_line()

  # If the api_client path was not specified, get it from the script path
  try:
    args.api_client = os.path.dirname(os.path.realpath(__file__)).split('api_client')[0] + str('api_client')
  except:
    fail('Could not get the api_client path from the command. Please specify using --api_client / -a')

  # Import the api client
  path.append(args.api_client)
  from mosaic import Mosaic, Project, Store
  api_store = Store(config_file = args.client_config)
  api_mosaic = Mosaic(config_file = args.client_config)

  # Add the project ids to a list
  project_ids = []
  if ',' in args.project_ids:
    for project_id in args.project_ids.split(','):
      project_ids.append(int(project_id))
  else:
    project_ids.append(int(args.project_ids))

  # Remove the user from the given projects
  api_mosaic.delete_user_project_roles(args.user_id, project_ids = project_ids)

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')

  # The user id
  parser.add_argument('--user_id', '-u', required = True, metavar = 'integer', help = 'The id of the user whose roles are to be deleted')

  # The projects to remove the user from
  parser.add_argument('--project_ids', '-p', required = True, metavar = 'string', help = 'A comma separated list of project ids to remove the user from')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
