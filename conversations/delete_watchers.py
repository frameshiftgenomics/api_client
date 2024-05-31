import os
import argparse

from sys import path

def main():

  # Parse the command line
  args = parseCommandLine()

  # Import the api client
  path.append(args.api_client)
  from mosaic import Mosaic, Project, Store
  apiStore  = Store(config_file = args.client_config)
  apiMosaic = Mosaic(config_file = args.client_config)

  # Open an api client project object for the defined project
  project = apiMosaic.get_project(args.project_id)

  # Get the user ids in an array
  user_ids = args.user_ids.split(',') if ',' in args.user_ids else [args.user_ids]

  # Delete watchers from the specified conversation
  project.delete_watchers(args.conversation_id, user_ids)

# Input options
def parseCommandLine():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = True, metavar = 'string', help = 'The api_client directory')

  # The project id
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The id of the project to delete')

  # The id of the conversation to remove watchers from
  parser.add_argument('--conversation_id', '-n', required = True, metavar = 'integer', help = 'The id of the conversation to remove watchers from')

  # A comma separated list of users to remove as watchers from the conversation
  parser.add_argument('--users', '-u', required = True, metavar = 'string', help = 'A comma separated list of users to remove as watchers from the conversation')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print(message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
