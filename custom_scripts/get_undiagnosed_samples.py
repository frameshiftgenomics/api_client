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

  # Get the project settings
  available_values = {}
  if args.values:
    requested_values = args.values.split(',') if ',' in args.values else [args.values]
    project_ids = []
  for attribute in project.get_project_attributes():
    if int(attribute['id']) == int(args.attribute_id):
      for value in attribute['values']:
        if not args.values:
          if value['value'] not in available_values:
            available_values[value['value']] = 1
          else:
            available_values[value['value']] += 1
        else:
          if value['value'] in requested_values:
            project_ids.append(str(value['project_id']))

  # If no value were provided, print out the available values
  if args.values:
    print(','.join(project_ids))
  else:
    for value in available_values:
      print(value, ': ', available_values[value], sep = '')

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = True, metavar = 'string', help = 'The api_client directory')

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # The attribute id to search on
  parser.add_argument('--attribute_id', '-i', required = True, metavar = 'integer', help = 'The Mosaic attribute id to query')

  # The attribute values to return projects for
  parser.add_argument('--values', '-v', required = False, metavar = 'string', help = 'A comma separated list of values. Projects with one of these values for the specified attribute will be returned')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print(message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
