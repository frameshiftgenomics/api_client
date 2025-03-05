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
  from mosaic import Mosaic, Project, Store
  api_store = Store(config_file = args.client_config)
  api_mosaic = Mosaic(config_file = args.client_config)

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # Check if this is a collection
  data = project.get_project()
  if not data['is_collection']:
    fail('Supplied project id (' + args.project_id + ') is for a project, not a collection')

  # Set the values to update
  reference = args.reference if args.reference else None
  privacy_level = args.privacy_level if args.privacy_level else None
  attribute_ids = []
  column_ids = []
  if args.project_table_columns:
    columns = args.project_table_columns.split(',') if ',' in args.project_table_columns else [args.project_table_columns]
  
    # Loop over the list of columns and check that they are attribute ids or one of an allowed set of values
    allowed_columns = ['NICKNAME', 'PHI_NAME', 'DESCRIPTION', 'ROLE', 'CREATED', 'UPDATED', 'COLLABORATORS', 'REFERENCE', 'VARIANT_COUNT', 'SAMPLE_COUNT', 'ID']
    for column_id in columns:
      if column_id in allowed_columns:
        column_ids.append(column_id)
      else:
        try:
          column_ids.append(int(column_id))
          attribute_ids.append(int(column_id))
        except:
          fail('Column ids must be one of the following allowed values, or a project attribute id (failed value: ' + str(column_id) + '):\n  ' + '\n  '.join(allowed_columns))

  # Update the project settings
  project.put_collection_project_settings(privacy_level = privacy_level, selected_collections_table_columns = column_ids, selected_collection_attributes = attribute_ids)

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # Optional arguments
  parser.add_argument('--privacy_level', '-l', required = False, metavar = 'string', help = 'The privacy level to assign to the project')
  parser.add_argument('--reference', '-r', required = False, metavar = 'string', help = 'The genome reference to assign to the project')
  parser.add_argument('--project_table_columns', '-t', required = False, metavar = 'string', help = 'A comma separated list of project attribute ids or uids')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
