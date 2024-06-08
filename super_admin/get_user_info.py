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

  # Get the user info
  print(apiMosaic.get_user_info(args.user_id))

# Input options
def parseCommandLine():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = True, metavar = 'string', help = 'The api_client directory')

  # The user id
  parser.add_argument('--user_id', '-i', required = True, metavar = 'integer', help = 'The user id')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print(message, sep = "")
  exit(1)

if __name__ == "__main__":
  main()
