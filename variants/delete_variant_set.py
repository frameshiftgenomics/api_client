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

  # Open an api client project object for the defined project
  project = apiMosaic.get_project(args.project_id)

  # Get the variant sets in the project
  variant_set_ids = [args.variant_set_ids] if ',' not in args.variant_set_ids else args.variant_set_ids.split(',')
  for variant_set_id in variant_set_ids:
    data = project.delete_variant_set(variant_set_id)

# Input options
def parseCommandLine():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = True, metavar = 'string', help = 'The api_client directory')

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to add variant filters to')

  # A comma separated list of variant set ids to delete
  parser.add_argument('--variant_set_ids', '-v', required = True, metavar = 'string', help = 'A comma separate list of variant set ids to delete')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print(message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
