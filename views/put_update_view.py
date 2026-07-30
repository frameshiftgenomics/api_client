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

  # Get a list of all attribute ids in the project. This can be regular project attributes,
  # data groups, or intervals
  project_attribute_ids = []
  for attribute_info in project.get_project_attribute_definitions():
    if attribute_info['id'] not in project_attribute_ids:
      project_attribute_ids.append(attribute_info['id'])

  # Loop over the list of attribute ids and ensure they exist in the project
  attribute_ids = None
  if args.attribute_ids:
    attribute_ids = args.attribute_ids.split(',') if ',' in args.attribute_ids else [args.attribute_ids]
    missing_ids = ''
    for attribute_id in attribute_ids:
      if int(attribute_id) not in project_attribute_ids:
        missing_ids += attribute_id + ','
    missing_ids = missing_ids.rstrip(',')
    if len(missing_ids) > 0:
      print('The following attribute ids are not in the selected project and so cannot be part of a view:')
      print('  ', missing_ids)
      exit(0)

  # Set the name and description
  name = args.name if args.name else None
  description = args.description if args.description else None

  # POST the new view
  try:
    project.put_update_view(args.view_type, args.view_id, name = name, description = description, selected_attribute_ids = attribute_ids)
  except Exception as e:
    fail('failed to PUT data group view. Error wes: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required
  optional_arguments = groups.optional

  # The project id
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # View information
  required_arguments.add_argument('--view_type', '-t', required = True, metavar = 'string', help = 'The type of view to update. Available options: data-groups')
  required_arguments.add_argument('--view_id', '-i', required = True, metavar = 'string', help = 'The id of the view to update')

  # Optional arguments
  optional_arguments.add_argument('--name', '-n', required = False, metavar = 'string', help = 'The name of the new data group view')
  optional_arguments.add_argument('--attribute_ids', '-ai', required = False, metavar = 'string', help = 'A comma separated list of attribute ids to appear in the view')

  # Optional arguments
  project_arguments.add_argument('--description', '-d', required = False, metavar = 'string', help = 'A description of the new data group view')

  return parser.parse_args()

if __name__ == "__main__":
  main()
