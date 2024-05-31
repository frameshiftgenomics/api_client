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
  apiMosaic = Mosaic(config_file = args.config)
  collection = apiMosaic.get_project(args.project_id)

  # Check if this is a collection
  data = collection.get_project()
  if not data['is_collection']:
    fail('Supplied project id (' + args.project_id + ') is for a project, not a collection')

  # Get the user ids in an array
  user_ids = args.user_ids.split(',') if ',' in args.user_ids else [args.user_ids]

  # Loop over the collection projects
  for project_info in data['collection_projects']:
    project_id = project_info['child_project_id']
    project = apiMosaic.get_project(project_id)
    print('Removing watchers from project ', str(project_id), ' - ', project.name, sep = '')

    # Get the conversations in the project
    conversations = project.get_project_conversations()
    if 'data' in conversations:
      for conversation in conversations['data']:
        try:
          project.delete_watchers(conversation['id'], user_ids)
        except:
          pass

# Input options
def parseCommandLine():
  global version
  parser = argparse.ArgumentParser(description='Process the command line')

  # Required arguments
  parser.add_argument('--config', '-c', required = True, metavar = 'string', help = 'The config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = True, metavar = 'string', help = 'The directory where the Python api wrapper lives')

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # A comma separated list of users to remove as watchers from the conversation
  parser.add_argument('--user_ids', '-u', required = True, metavar = 'string', help = 'A comma separated list of users to remove as watchers from the conversation')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print(message, sep = '')
  exit(1)

# Throw a warning
def warning(message):
  print('WARNING: ', message, sep = '')

# Initialise global variables

# Pipeline version
version = "0.0.1"

if __name__ == "__main__":
  main()
