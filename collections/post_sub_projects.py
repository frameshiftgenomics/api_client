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
  collection = api_mosaic.get_project(args.project_id)

  # Check that this is a collection
  if not collection.data['is_collection']:
    fail('Supplied project id (' + args.project_id + ') needs to be the id of a collection')

  # Add the projects to the collection
  projects_to_add = []
  for udn_id in args.projects_to_add.split(','):
    projects_to_add.append(str(udn_id))
  data = collection.post_sub_projects(collection_projects = projects_to_add, same_role = 'true')

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

  # The project id of the collection to add projects to
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id of the collection to add projects to')

  # The name of the sample to add
  parser.add_argument('--projects_to_add', '-r', required = True, metavar = 'string', help = 'A comma separated list of projects to add to the collection')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
