import os
import argparse

from pprint import pprint
from sys import path

def main():

  # Parse the command line
  args = parse_command_line()

  # Import the api client
  path.append(args.api_client)
  from mosaic import Mosaic, Project, Store
  api_store = Store(config_file = args.client_config)
  api_mosaic = Mosaic(config_file = args.client_config)

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # Check if this is a collection
  data = project.get_project()
  if data['is_collection']:
    project_ids = []
    for project_id in data['collection_project_ids']:
      project_ids.append(project_id)
  else:
    project_ids = [args.project_id]

  # Loop over all projects
  for project_id in project_ids:
    project = api_mosaic.get_project(project_id)
    print('Checking project: ', project.name, sep = '')

    # Get all project files
    for project_file in project.get_project_files():
      extension = project_file['name'].rsplit('.')[-1]
      if str(extension) == str(args.extension):
        project.put_project_file(project_file['id'], file_type = extension)

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = True, metavar = 'string', help = 'The api_client directory')

  # The project id
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id')

  # Convert files with this extension
  parser.add_argument('--extension', '-e', required = True, metavar = 'string', help = 'The extension to set. Files that have this extension will have their type set to this')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print(message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
