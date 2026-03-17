import os
import argparse

from sys import path
from pprint import pprint

def main():
  global allowed_references
  global system_projects

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

  if args.reference:
    if args.reference not in allowed_references:
      fail('Unknown reference genome: ' + str(args.reference))

  # Get all the available projects
  for project_info in api_mosaic.get_projects(search = args.search):
    display = True
    if args.reference:
      display = False
    variant_count = 0 if not project_info['variant_count'] else project_info['variant_count']
    if args.min_variants:
      if int(variant_count) < int(args.min_variants):
        display = False
    if args.max_variants:
      if int(variant_count) > int(args.max_variants):
        display = False

    # Ignore template
    if project_info['is_template']:
      display = False

    # Ignore collections
    if project_info['is_collection']:
      display = False

    # Ignore system projects. This is the Public Attributes, Mosaic <REF> Globals projects
    if project_info['name'] in system_projects:
      display = False

    # Write out information
    if display:
      print(project_info['name'], project_info['variant_count'])

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

  # Only output projects of a given reference
  project_arguments.add_argument('--reference', '-r', required = False, metavar = 'string', help = 'Only output projects with the specified reference')

  # Query params
  optional_arguments.add_argument('--search', '-s', required = False, metavar = 'string', help = 'Term to search on')

  # Display params
  display_arguments.add_argument('--min_variants', '-min', required = False, metavar = 'integer', help = 'Only output projects with a minimum of this number of variants')
  display_arguments.add_argument('--max_variants', '-max', required = False, metavar = 'integer', help = 'Only output projects with a maximum of this number of variants')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

allowed_references = []
allowed_references.append('GRCh37')
allowed_references.append('GRCh38')

system_projects = []
system_projects.append('Public Attributes')
system_projects.append('Mosaic Globals')
system_projects.append('Mosaic GRCh37 Globals')
system_projects.append('Mosaic GRCh38 Globals')

if __name__ == "__main__":
  main()
