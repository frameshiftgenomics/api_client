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
  api_store  = Store(config_file = args.client_config)
  api_mosaic = Mosaic(config_file = args.client_config)

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # Get the variant sets in the project
  data = project.get_variant_watchlist(args.include_variant_data)

  # Format the output based on whether variants were output
  print(data['name'], ': ', data['id'], sep = '')
  print('  description: ', data['description'], sep = '')
  print('  is_watchlist: ', data['is_watchlist'], sep = '')
  print('  is_public_to_project: ', data['is_public_to_project'], sep = '')
  print('  Number of variants: ', len(data['variant_ids']), sep = '')

# Input options
def parseCommandLine():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = True, metavar = 'string', help = 'The api_client directory')

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to add variant filters to')

  # Should variant data be returned
  parser.add_argument('--include_variant_data', '-i', required = False, action = 'store_true', help = 'Should variant data be returned')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print(message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
