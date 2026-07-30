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
  existing_view_ids = ['DEFAULT']
  for view in project.get_views(args.view_type):
    existing_view_ids.append(str(view['id']))

  # Put the view ids into a list, checking they are all present in the project
  view_ids = args.view_ids.split(',') if ',' in args.view_ids else [args.view_ids]
  for view_id in view_ids:
    if str(view_id) not in existing_view_ids:
      fail('view id ' + str(view_id) + ' is not present in the project')

  # Update the views tabs
  try:
    project.put_upsert_views_tabs(args.view_type, view_ids)
  except Exception as e:
    fail('failed to PUT data group views tabs. Error wes: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required

  # The project id
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # View information
  required_arguments.add_argument('--view_type', '-t', required = True, metavar = 'string', help = 'The type of view tabs to update. Available options: data-groups')
  required_arguments.add_argument('--view_ids', '-i', required = True, metavar = 'string', help = 'A comma separate list of view ids')

  return parser.parse_args()

if __name__ == "__main__":
  main()
