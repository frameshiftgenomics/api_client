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
  api_store  = Store(config_file = args.client_config)
  api_mosaic = Mosaic(config_file = args.client_config)

#  # Get the attributes ids into a list
#  attribute_ids = None
#  if args.attribute_ids:
#    attribute_ids = args.attribute_ids.split(',') if ',' in args.attribute_ids else [int(args.attribute_ids)]

  # Get the attributes available for import
  for attribute in api_mosaic.get_public_project_attributes():#attribute_ids = attribute_ids):
    print(attribute['id'], ': ', attribute['name'], sep = '')

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = True, metavar = 'string', help = 'The api_client directory')

  # An optional list of attributes ids
  #parser.add_argument('--attribute_ids', '-i', required = False, metavar = 'string', help = 'An optional comma separated list of attribute ids to query')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print(message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
