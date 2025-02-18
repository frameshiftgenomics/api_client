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
  from mosaic import Mosaic, Project, Store
  api_store = Store(config_file = args.client_config)
  api_mosaic = Mosaic(config_file = args.client_config)

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # Import tha annotation
  data = project.put_variant_annotation(args.annotation_id, name = args.name, value_type = args.type, privacy_level = args.privacy_level, display_type = args.display_type, severity = args.severity, category = args.category, value_truncate_type = args.value_truncate_type, value_max_length = args.value_max_length, latest_version_id = args.latest_version_id)

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # The annotation id to update
  parser.add_argument('--annotation_id', '-i', required = True, metavar = 'integer', help = 'The Mosaic annotation id to import')

  # Optional values to update
  parser.add_argument('--name', '-n', required = False, metavar = 'string', help = 'The name of the annotation')
  parser.add_argument('--type', '-t', required = False, metavar = 'string', help = 'The type of the annotation')
  parser.add_argument('--privacy_level', '-l', required = False, metavar = 'string', help = 'The privacy level of the annotation')
  parser.add_argument('--display_type', '-d', required = False, metavar = 'string', help = 'The display type of the annotation')
  parser.add_argument('--severity', '-s', required = False, metavar = 'string', help = 'The severity of the annotation')
  parser.add_argument('--category', '-g', required = False, metavar = 'string', help = 'The category of the annotation')
  parser.add_argument('--value_truncate_type', '-v', required = False, metavar = 'string', help = 'The method of truncating the annotation values')
  parser.add_argument('--value_max_length', '-m', required = False, metavar = 'string', help = 'The max length of the of the annotation values')

  # Set the latest version
  parser.add_argument('--latest_version_id', '-e', required = False, metavar = 'integer', help = 'The annotation version id to set as the latest version')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
