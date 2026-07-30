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

  # Check that this is a collection
  if not project.get_project()['is_collection']:
    fail('This endpoint is only for collections')

  # Get a list of all attribute ids in the project. This can be regular project attributes,
  # data groups, or intervals
  project_attribute_ids = []
  for attribute_info in project.get_project_attribute_definitions():
    if attribute_info['id'] not in project_attribute_ids:
      project_attribute_ids.append(attribute_info['id'])

  # Loop over the list of attribute ids and ensure they exist in the project
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

  # Set the description
  description = args.description if args.description else None

  # If an icon is given, make sure it begins with 'mdi-'
  icon = None
  if args.icon:
    icon = 'mdi-' + args.icon if not args.icon.startswith('mdi-') else args.icon

  # Check for attribute filters and pagination options
  attribute_filters = args.attribute_filters if args.attribute_filters else None
  pagination = args.pagination if args.pagination else None

  # POST the new view
  try:
    project.post_create_collection_projects_view(args.name, description = description, icon = icon, selected_attribute_ids = attribute_ids, attribute_filters = attribute_filters, pagination = pagination)
  except Exception as e:
    fail('failed to POST new data group view. Error wes: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required
  optional_arguments = groups.optional

  # The project id
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # Required arguments
  required_arguments.add_argument('--name', '-n', required = True, metavar = 'string', help = 'The name of the new data group view')
  required_arguments.add_argument('--attribute_ids', '-ai', required = True, metavar = 'string', help = 'A comma separated list of attribute ids to appear in the view')

  # Optional arguments
  optional_arguments.add_argument('--attribute_filters', '-af', required = False, metavar = 'string', help = 'Attribute filters. This is a json object of the form: [{"uid": "attribute_uid", "value_type": "string", "values": ["VALUE"]}]')
  optional_arguments.add_argument('--pagination', '-pg', required = False, metavar = 'string', help = 'Paginsation settings. This is a json object of the form: {"descending": "false", "page": 1, "rowsPerPage": 10, "sortBy": "attribute_uid"}')
  optional_arguments.add_argument('--description', '-d', required = False, metavar = 'string', help = 'A description of the new data group view')
  optional_arguments.add_argument('--icon', '-o', required = False, metavar = 'string', help = 'An icon for the view')

  return parser.parse_args()

if __name__ == "__main__":
  main()
