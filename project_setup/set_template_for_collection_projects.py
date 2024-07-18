import os
import argparse
import json
import sys

from os.path import exists
from pprint import pprint
from sys import path

def main():
  global version

  # Parse the command line
  args = parseCommandLine()

  # Import the api client
  path.append(args.api_client)
  from mosaic import Mosaic, Project, Store
  store = Store(config_file = args.config)
  api_mosaic = Mosaic(config_file = args.config)

  # Check that the supplied project id is for a collection
  collection = api_mosaic.get_project(args.project_id)
  data = collection.get_project()
  if not data['is_collection']:
    fail('Supplied project id (' + args.project_id + ') is for a project, not a collection')

  # Loop over all projects in the collection
  for project_info in collection.get_collection_projects():
    project_id = project_info['id']
    print('Applying template to project ' + project_info['name'] + ', id: ' + str(project_id))

    # Open the project and apply the template
    project = api_mosaic.get_project(project_id)
    data = project.patch_project(args.template_id)

# Input options
def parseCommandLine():
  parser = argparse.ArgumentParser(description='Process the command line')

  # Required arguments
  parser.add_argument('--config', '-c', required = True, metavar = 'string', help = 'The config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = True, metavar = 'string', help = 'The directory where the Python api wrapper lives')

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # The project id of the template project
  parser.add_argument('--template_id', '-t', required = True, metavar = 'integer', help = 'The Mosaic project id of the template project')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

# Throw a warning
def warning(message):
  print('WARNING: ', message, sep = '')

# Initialise global variables

if __name__ == "__main__":
  main()
