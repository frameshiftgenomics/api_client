import os
import argparse

from sys import path

def main():

  # Parse the command line
  args = parse_command_line()

  # If the api_client path was not specified, get it from the script path
  if not args.api_client:
    try:
      args.api_client = os.path.dirname(os.path.realpath(__file__)).split('api_client')[0] + str('api_client')
    except:
      fail('Could not get the api_client path from the command. Please specify using --api_client / -a')

  # Import the api client
  path.append(args.api_client)
  try:
    from mosaic import Mosaic, Project, Store
  except:
    fail('Cannot find mosaic. Please set the --api_client / -a argument')
  api_store = Store(config_file = args.client_config)
  api_mosaic = Mosaic(config_file = args.client_config)

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # If categories were supplied, break up the list
  categories = []
  if args.categories:
    categories = args.categories.split(',') if ',' in args.categories else [args.categories]

  # Get the list of variant filter ids
  for variant_filter in project.get_variant_filters():
    display = True
    if args.categories and variant_filter['category'] not in categories:
      display = False

    # Only display if the filter is in a specified category, or no categories were specified
    if display:
      if args.display_all:
        print(variant_filter['name'])
        for field in variant_filter:
          if field != 'name':
            print('  ', field, ': ', variant_filter[field], sep = '')
      else:
        print(variant_filter['id'])

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')
  api_arguments = parser.add_argument_group('API Arguments')
  project_arguments = parser.add_argument_group('Project Arguments')
  required_arguments = parser.add_argument_group('Required Arguments')
  optional_arguments = parser.add_argument_group('Optional Arguments')
  display_arguments = parser.add_argument_group('Display Information')

  # Define the location of the api_client and the ini config file
  api_arguments.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  api_arguments.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to add variant filters to')

  # Display options
  display_arguments.add_argument('--display_all', '-da', required = False, action = 'store_true', help = 'Output all variant filter information')
  display_arguments.add_argument('--categories', '-ca', required = False, metavar = 'string', help = 'Comma separated list of categories. Only filters in these categories will be returned')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
