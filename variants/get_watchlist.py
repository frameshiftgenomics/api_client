import os
import argparse
from pprint import pprint

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
  try:
    project = api_mosaic.get_project(args.project_id)
  except Exception as e:
    fail('Failed to open project. Error was: ' + str(e))

  # Get the variant sets in the project
  include_variant_data = 'true' if args.include_variant_data else 'false'
  try:
    data = project.get_variant_watchlist(include_variant_data = include_variant_data)
  except Exception as e:
    fail('Failed to get variant watchlist. Error was: ' + str(e))

  # If only the number of variants is required
  if args.output_number_variants:
    print(len(data['variant_ids']))

  # Format the output based on whether variants were output
  else:
    print(data['name'], ': ', data['id'], sep = '')
    print('  description: ', data['description'], sep = '')
    print('  is_watchlist: ', data['is_watchlist'], sep = '')
    print('  is_public_to_project: ', data['is_public_to_project'], sep = '')
    print('  Number of variants: ', len(data['variant_ids']), sep = '')

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

  # Should variant data be returned
  optional_arguments.add_argument('--include_variant_data', '-i', required = False, action = 'store_true', help = 'Should variant data be returned')

  # Display options
  display_arguments.add_argument('--output_number_variants', '-nv', required = False, action = 'store_true', help = 'Only output the number of variants in the watchlist')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
