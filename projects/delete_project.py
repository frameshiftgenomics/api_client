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
  #project = apiMosaic.get_project(args.project_id)

  # Delete the attribute form
  apiMosaic.delete_project(args.project_id)

# Input options
def parseCommandLine():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = True, metavar = 'string', help = 'The api_client directory')

  # The id of the attribute form to delete
  parser.add_argument('--project_id', '-p', required = True, metavar = 'string', help = 'The id of the project to delete')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print(message, sep = "")
  exit(1)

if __name__ == "__main__":
  main()
