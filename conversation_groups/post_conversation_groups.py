import os
import argparse

from pprint import pprint
from sys import path

def main():

  # Parse the command line
  args = parseCommandLine()

  # Import the api client
  path.append(args.api_client)
  from mosaic import Mosaic, Project, Store
  apiStore  = Store(config_file = args.client_config)
  apiMosaic = Mosaic(config_file = args.client_config)

  # Create a new conversation group
  description = args.description if args.description else None
  user_ids = args.user_ids.split(',') if ',' in args.user_ids else [args.user_ids]
  data = apiMosaic.post_conversation_groups(args.name, description, user_ids)

# Input options
def parseCommandLine():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = True, metavar = 'string', help = 'The api_client directory')

  # Get information on the conversation group
  parser.add_argument('--name', '-n', required = True, metavar = 'string', help = 'The name of the conversation group')
  parser.add_argument('--description', '-d', required = False, metavar = 'string', help = 'A description of the conversation group')
  parser.add_argument('--user_ids', '-u', required = True, metavar = 'string', help = 'A comma separated list of user ids to add to the conversation group')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print(message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
