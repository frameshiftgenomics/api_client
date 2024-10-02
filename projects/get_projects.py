import os
import argparse

from sys import path

def main():
  global allowed_references

  # Parse the command line
  args = parse_command_line()

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
  parser.add_argument('--api_client', '-a', required = True, metavar = 'string', help = 'The api_client directory')

  # Only output project ids
  parser.add_argument('--output_ids_only', '-o', required = False, action = 'store_true', help = 'If set, only the project ids will be output')

  # Only output projects of a given reference
  parser.add_argument('--reference', '-r', required = False, metavar = 'string', help = 'Only output projects with the specified reference')

  # Query params
  parser.add_argument('--search', '-s', required = False, metavar = 'string', help = 'Term to search on')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print(message, sep = '')
  exit(1)

allowed_references = []
allowed_references.append('GRCh37')
allowed_references.append('GRCh38')

if __name__ == "__main__":
  main()
