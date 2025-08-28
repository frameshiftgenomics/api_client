import os
import argparse

from pprint import pprint
from sys import path

def main():

  # Parse the command line
  args = parse_command_line()

  # If the api_client path was not specified, get it from the script path
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

  # Set the values to update
  reference = args.reference if args.reference else None
  privacy_level = args.privacy_level if args.privacy_level else None
  is_template = args.is_template if args.is_template else None
  external_url = args.external_url if args.external_url else None

  # Set the sub-project template ids
  if args.sub_project_template_ids:
    sub_project_template_ids = args.sub_project_template_ids.split(',') if ',' in args.sub_project_template_ids else [args.sub_project_template_ids]
  else:
    sub_project_template_ids = None

  # Update the project settings
  project.put_project_settings(external_url = external_url, \
                               privacy_level = privacy_level, \
                               reference = reference, \
                               selected_sample_attribute_chart_data = None, \
                               selected_sample_attribute_column_ids = None, \
                               selected_variant_annotation_version_ids = None, \
                               default_variant_set_annotation_ids = None, \
                               sorted_annotations = None, \
                               is_template = is_template, \
                               sub_project_template_ids = sub_project_template_ids)

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
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # Optional arguments
  optional_arguments.add_argument('--external_url', '-e', required = False, metavar = 'string', help = 'The project\'s external url')
  optional_arguments.add_argument('--privacy_level', '-l', required = False, metavar = 'string', help = 'The privacy level to assign to the project')
  optional_arguments.add_argument('--reference', '-r', required = False, metavar = 'string', help = 'The genome reference to assign to the project')
  optional_arguments.add_argument('--is_template', '-t', required = False, action='store_true', help = 'Select if the project should be a template project')
  optional_arguments.add_argument('--sub_project_template_ids', '-s', required = False, metavar='string', help = 'A comma separated list of project ids to add to a collection')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
