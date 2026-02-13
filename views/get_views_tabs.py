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

  # Define the allowed object types
  allowed_view_types = {'data-groups'}
  if args.view_type not in allowed_view_types:
    fail('type is unknown. Allowed types are: ' + ', '.join(allowed_view_types))

  # Get all of the views in the project
  views = {}
  for view in project.get_views(args.view_type):
    views[str(view['id'])] = view['name']

  # Get the available view tabs
  try:
    for view_id in project.get_views_tabs(args.view_type)['view_ids']:
      name = views[str(view_id)] if str(view_id) in views else view_id
      if name == 'DEFAULT':
        name = 'All'
      print('name: ', name, ', id: ', view_id, sep = '')
  except Exception as e:
    fail('failed to get view tabs. Error was: ' + str(e))

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

  # View information
  required_arguments.add_argument('--view_type', '-t', required = True, metavar = 'string', help = 'The type of view to get. Available options: data-group')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
