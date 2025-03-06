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
  from mosaic import Mosaic, Project, Store
  api_store = Store(config_file = args.client_config)
  api_mosaic = Mosaic(config_file = args.client_config)

  if args.reference:
    if args.reference not in allowed_references:
      fail('Unknown reference genome: ' + str(args.reference))

  # Get all the available projects
  for project_info in api_mosaic.get_projects(search = args.search):
    display = True
    if args.reference:
      if project_info['reference'] != args.reference:
        display = False

    # Ignore template projects unless told otherwise
    if project_info['is_template']:
      if not args.include_templates:
        display = False

    # Ignore collections unless told otherwise
    if project_info['is_collection']:
      if not args.include_collections:
        display = False

    # By default ignore system projects. This is the Public Attributes, Mosaic <REF> Globals projects
    if project_info['name'] in system_projects:
      if not args.include_system_projects:
        display = False

    # Write out information
    if display:
      if args.output_ids_only:
        print(project_info['id'], sep = '')
      else:
        print(project_info['name'], ': ', project_info['id'], sep = '')

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

  # Only output project ids, or exclude specific projects
  parser.add_argument('--output_ids_only', '-o', required = False, action = 'store_true', help = 'If set, only the project ids will be output')
  parser.add_argument('--include_templates', '-t', required = False, action = 'store_true', help = 'By default, template projects will NOT be included in the output. This will include them')
  parser.add_argument('--include_collections', '-i', required = False, action = 'store_true', help = 'By default, collections will NOT be included in the output. This will include them')
  parser.add_argument('--include_system_projects', '-n', required = False, action = 'store_true', help = 'By default, system projects (Public Attribute, Globals) will NOT be included in the output. This willi include them')

  # Only output projects of a given reference
  parser.add_argument('--reference', '-r', required = False, metavar = 'string', help = 'Only output projects with the specified reference')

  # Query params
  parser.add_argument('--search', '-s', required = False, metavar = 'string', help = 'Term to search on')

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
