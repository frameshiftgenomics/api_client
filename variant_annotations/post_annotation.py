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
  project = api_mosaic.get_project(args.project_id)

  # Check the inputted information
  allowed_types = ['float', 'string']
  if args.value_type not in allowed_types:
    fail('ERROR: the supplied value_type (' + str(args.value_type) + ') is invalid. Allowed values are: ' + ','.join(allowed_types))
  if args.privacy_level != 'public' and args.privacy_level != 'private':
    fail('ERROR: unknown privacy_level. Must be public or private')

  # Create the new annotation
  data = project.post_variant_annotation(name=args.name, value_type=args.value_type, privacy_level=args.privacy_level, display_type=None, severity=None, category=args.category, value_truncate_type=None, value_max_length=None)

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # Information about the annotation being created
  parser.add_argument('--name', '-n', required = True, metavar = 'string', help = 'The annotation name')
  parser.add_argument('--category', '-t', required = True, metavar = 'string', help = 'The category to assign the annotation to')
  parser.add_argument('--value_type', '-v', required = True, metavar = 'string', help = 'The annotation type: string or float')
  parser.add_argument('--privacy_level', '-y', required = True, metavar = 'string', help = 'The annotation privacy: public or private')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
