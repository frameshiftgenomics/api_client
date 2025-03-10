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

  # Check if this is a collection
  data = project.get_project()
  if data['is_collection']:
    project_ids = []
    for sub_project in data['collection_projects']:
      project_ids.append(sub_project['child_project_id'])
  else:
    project_ids = [args.project_id]

  # Get the list of annotation ids to delete
  annotation_ids = args.annotation_ids.split(',') if ',' in args.annotation_ids else [args.annotation_ids]

  # Loop over all the projects
  for project_id in project_ids:
    print('Deleting annotations in project ', project.name, ': ', project_id, sep = '')
    project = api_mosaic.get_project(project_id)

    # Delete the annotations
    for annotation_id in annotation_ids:
      try:
        data = project.delete_variant_annotation(annotation_id)
      except:
        pass

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to get annotations for')

  # A comma separated list of annotation ids to delete
  parser.add_argument('--annotation_ids', '-i', required = True, metavar = 'string', help = 'A comma separated list of annotation ids to delete')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
