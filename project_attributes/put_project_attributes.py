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
  api_store  = Store(config_file = args.client_config)
  api_mosaic = Mosaic(config_file = args.client_config)

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # Set the display type
  allowed_display_types = ['time', 'date', 'duration', 'custom']
  if args.display_type:
    if args.display_type not in allowed_display_types:
      fail('unknown display type: ' + args.display_type)
    display_type = args.display_type
  else:
    display_type = None

  # Get the project settings
  is_editable = 'false' if args.is_editable else 'true'
  values = args.predefined_values.split(',') if args.predefined_values else None
  data = project.put_project_attributes(args.attribute_id, description=args.description, name=args.name, predefined_values=values, is_editable=is_editable, display_type=display_type, value=args.value)

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')
  parser.add_argument('--attribute_id', '-t', required = True, metavar = 'integer', help = 'The Mosaic attribute id to update')

  # Optional arguments to update
  parser.add_argument('--description', '-d', required = False, metavar = 'string', help = 'The attribute description')
  parser.add_argument('--display_type', '-s', required = False, metavar = 'string', help = 'The display type for the attribute: time, date, duration, custom')
  parser.add_argument('--name', '-n', required = False, metavar = 'string', help = 'The name of the attribute')
  parser.add_argument('--is_editable', '-e', required = False, action = 'store_true', help = 'If set, the attribute will not be editable')
  parser.add_argument('--predefined_values', '-r', required = False, metavar = 'string', help = 'A comma separated list of values that will be available by default')
  parser.add_argument('--value', '-v', required = False, metavar = 'string', help = 'The value of the attribute')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
