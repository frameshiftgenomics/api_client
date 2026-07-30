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
  allowed_view_types = {'data-groups'}
  if args.view_type not in allowed_view_types:
    fail('type is unknown. Allowed types are: ' + ', '.join(allowed_view_types))

  # Get all of the views in the project
  views = {}
  for view in project.get_views(args.view_type):
    views[str(view['id'])] = view['name']

  # Get the available view tabs
  try:
    for view_id in project.get_views_tabs(args.view_type)['view_ids']:
      name = views[str(view_id)] if str(view_id) in views else view_id
      if name == 'DEFAULT':
        name = 'All'
      print('name: ', name, ', id: ', view_id, sep = '')
  except Exception as e:
    fail('failed to get view tabs. Error was: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required

  # The project id
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # View information
  required_arguments.add_argument('--view_type', '-t', required = True, metavar = 'string', help = 'The type of view to get. Available options: data-groups')

  return parser.parse_args()

if __name__ == "__main__":
  main()
