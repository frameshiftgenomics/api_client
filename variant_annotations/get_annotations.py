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
  annotation_ids = []
  if args.annotation_ids:
    annotation_ids = args.annotation_ids.split(',')

  #for annotation in project.get_variant_annotations(annotation_ids = annotation_ids):
  for annotation in project.get_variant_annotations():
    if args.name:
      if args.name == annotation['name']:
        if args.verbose:
          print_verbose(annotation)
        else:
          print(annotation['id'])
    else:
      if args.verbose:
        print_verbose(annotation)
      else:
        print_simple(annotation)

def print_simple(annotation):
  print(annotation['name'], ': ', annotation['id'], sep = '')

def print_verbose(annotation):
  print(annotation['name'], ' (id: ', annotation['id'], ')', sep = '')
  print('    uid: ', annotation['uid'], sep = '')
  print('    versions: ')
  for version in annotation['annotation_versions']:
    print('        ', version['version'], ': ', version['id'], sep = '')
  print('    privacy_level: ', annotation['privacy_level'], sep = '')
  print('    value_type: ', annotation['value_type'], sep = '')
  print('    display_type: ', annotation['display_type'], sep = '')
  print('    severity: ', annotation['severity'], sep = '')
  print('    category: ', annotation['category'], sep = '')

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = True, metavar = 'string', help = 'The api_client directory')

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to get annotations for')

  # If a name is supplied, just show information on the annotation with this name
  parser.add_argument('--name', '-n', required = False, metavar = 'string', help = 'If an annotation name is provided, information on this annotations will be shown')

  # If a list of annotation ids is supplied, only show results for these annotations
  parser.add_argument('--annotation_ids', '-i', required = False, metavar = 'string', help = 'An optional comman separated list of annotation ids to return')

  # Verbose output
  parser.add_argument('--verbose', '-v', required = False, action = 'store_true', help = 'Provide a verbose output')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print(message, sep = "")
  exit(1)

if __name__ == "__main__":
  main()
