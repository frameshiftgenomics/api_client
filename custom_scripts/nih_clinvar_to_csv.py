import os
import argparse
import json
import sys

from os.path import exists
from pprint import pprint
from sys import path

def main():

  # Parse the command line
  args = parse_command_line()

  # Import the api client
  path.append(args.api_client)
  from mosaic import Mosaic, Project, Store
  api_store = Store(config_file = args.config)
  api_mosaic = Mosaic(config_file = args.config)
  project = api_mosaic.get_project(args.project_id)

  # Check if this is a collection
  data = project.get_project()
  if data['is_collection']:
    project_ids = []
    for project_id in data['collection_project_ids']:
      project_ids.append(project_id)
    print('Getting ClinVar variants to review for projects in collection: ', data['name'], sep = '')
  else:
    project_ids = [args.project_id]
    print('Getting ClinVar variants to review for project: ', data['name'], sep = '')

  # Open the output csv file
  output = open(args.output_file, 'w')
  print('#project_name,project_id,url', file = output)

  # Loop over all the projects (for a collection) and apply the filters
  for project_id in project_ids:
    project = api_mosaic.get_project(project_id)

    # Get the unreviewed ClinVar tasks unless all ClinVar are requested
    for task in project.get_project_tasks():
      if task['type'] == 'primary_clinvar_review':
        if not task['completed'] or args.include_reviewed:
          url = 'https://udn.mosaic.frameshift.io/#/projects/' + str(project_id) + '/variants?variant_set_id=' + str(task['variant_set_id'])
          print(project.name, project_id, url, sep = ',', file = output)

  # Close the output file
  output.close()

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line')

  # Required arguments
  parser.add_argument('--config', '-c', required = True, metavar = 'string', help = 'The config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = True, metavar = 'string', help = 'The directory where the Python api wrapper lives')

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # The name of the output csv
  parser.add_argument('--output_file', '-o', required = True, metavar = 'string', help = 'The name of the output csv file')

  # Option to also consider completed tasks
  parser.add_argument('--include_reviewed', '-i', required = False, action = 'store_true', help = 'If set, include tasks marked as completed. By default ClinVar tasks that have not been completed will be considered')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print(message, sep = '')
  exit(1)

# Throw a warning
def warning(message):
  print('WARNING: ', message, sep = '')

# Initialise global variables

if __name__ == "__main__":
  main()
