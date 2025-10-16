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

  # Set the display requirements
  include_variant_data = True if args.show_variant_data else False
  include_genotype_data = True if args.show_genotype_information else False

  # Get the variant set information
  try:
    print(include_variant_data, include_genotype_data)
    print(project.get_variant_set(args.variant_set_id, include_variant_data = include_variant_data, include_genotype_data = include_genotype_data))
  except Exception as e:
    fail('Failed to get variant set information. Error was: ' + str(e))

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
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to get variants sets for')

  # Variant set information
  required_arguments.add_argument('--variant_set_id', '-v', required = True, metavar = 'integer', help = 'The Mosaic variant set id')

  # Optional arguments
  display_arguments.add_argument('--show_variant_data', '-si', required = False, action = 'store_true', help = 'Show the variant annotation information')
  display_arguments.add_argument('--show_genotype_information', '-sg', required = False, action = 'store_true', help = 'Show the genotype information')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
