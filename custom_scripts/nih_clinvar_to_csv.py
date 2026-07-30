import os
import json
import sys
import time

from os.path import exists
from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, warning, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)
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

  for task in api_mosaic.get_tasks(categories = None, completed = None, project_ids = project_ids, types = None, order_dir = None):
    url = 'https://udn.mosaic.frameshift.io/#/projects/' + str(task['project_id']) + '/variants?variant_set_id=' + str(task['variant_set_id'])
    print(task['project_name'], task['project_id'], url, sep = ',', file = output)

  # Close the output file
  output.close()

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # The name of the output csv
  parser.add_argument('--output_file', '-o', required = True, metavar = 'string', help = 'The name of the output csv file')

  # Option to also consider completed tasks
  parser.add_argument('--include_reviewed', '-i', required = False, action = 'store_true', help = 'If set, include tasks marked as completed. By default ClinVar tasks that have not been completed will be considered')

  return parser.parse_args()

# Throw a warning
def warning(message):
  print('WARNING: ', message, sep = '')

# Initialise global variables

if __name__ == "__main__":
  main()
