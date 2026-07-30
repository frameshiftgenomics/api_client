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
    for view in project.get_views(args.view_type):

      # Format the time stringd
      format_string = "%Y-%m-%dT%H:%M:%S.%fZ"
      created_at = str(datetime.strptime(view['created_at'], format_string)).split('.')[0]
      updated_at = str(datetime.strptime(view['updated_at'], format_string)).split('.')[0]

      print('name: ', view['name'], ', id: ', view['id'], sep = '')
      print('  type: ', view['type'], sep = '')
      print('  description: ', view['description'], sep = '')
      print('  created at: ', created_at, sep = '')
      print('  updated at: ', updated_at, sep = '')
      print('  icon: ', view['icon'], sep = '')

      # Write out information specific to data group views
      if args.view_type == 'data-groups':
        print('  data group id: ', view['project_view_data_group']['data_group_attribute_id'], sep = '')
        attribute_string = ''
        for attribute_id in view['project_view_data_group']['selected_attribute_ids']:
          attribute_string += str(attribute_id) + ', '
        print('  attribute ids: ', attribute_string.rstrip().rstrip(','), sep = '')
  except Exception as e:
    fail('failed to get view. Error was: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # View information
  required_arguments.add_argument('--view_type', '-t', required = True, metavar = 'string', help = 'The type of views to get. Available options: data-groups, collection-projects')

  return parser.parse_args()

if __name__ == "__main__":
  main()
