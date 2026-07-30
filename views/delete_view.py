import os
import sys
import time

from datetime import datetime
from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Open an api client project object for the defined project
  try:
    project = api_mosaic.get_project(args.project_id)
  except Exception as e:
    fail('Failed to open project. Error was: ' + str(e))

  # Define the allowed object types
  allowed_view_types = {'data-groups', 'collection-projects'}
  if args.view_type not in allowed_view_types:
    fail('type is unknown. Allowed types are: ' + ', '.join(allowed_view_types))

  # Get the available view tabs
  try:
    project.delete_view(args.view_type, args.view_id)
  except Exception as e:
    fail('failed to delete view. Error was: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required

  # The project id
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # View information
  required_arguments.add_argument('--view_type', '-t', required = True, metavar = 'string', help = 'The type of view to delete. Available options: data-groups, collection-projects')
  required_arguments.add_argument('--view_id', '-i', required = True, metavar = 'string', help = 'The id of the view to delete')

  return parser.parse_args()

if __name__ == "__main__":
  main()
