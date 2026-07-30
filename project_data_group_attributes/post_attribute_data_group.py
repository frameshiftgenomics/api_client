import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # Check the optional attributes
  name = args.name if args.name else None
  description = args.description if args.description else None
  is_public = 'true' if args.is_public else 'false'
  is_editable = 'true' if args.is_editable else 'false'

  # Generate a list of attribute ids
  if args.attributes:
    attribute_ids = [int(attribute_id) for attribute_id in args.attributes.split(',')] if ',' in args.attributes else [int(args.attributes)]
  else:
    attribute_ids = []

  # Check that all the attributes are in the project and are longitudinal
  project_attributes = {}
  attribute_array = []
  for project_attribute in project.get_project_attributes():
    project_attributes[str(project_attribute['id'])] = project_attribute['is_longitudinal']
  for attribute_id in attribute_ids:
    if str(attribute_id) not in project_attributes:
      fail('Attribute id ' + str(attribute_id) + ' is not in the project and so cannot be added to the data group')
    if not project_attributes[str(attribute_id)]:
      fail('Attribute id ' + str(attribute_id) + ' is not a longitudinal attribute and so cannot be added to the data group')
    attribute_array.append({"attribute_id": int(attribute_id)})

  # Edit the data group attribute
  project.post_attribute_data_groups(args.name, description = description, is_public = is_public, is_editable = is_editable, data_group_attributes = attribute_array)

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required
  optional_arguments = groups.optional

  # The project and attribute ids
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')
  project_arguments.add_argument('--attributes', '-i', required = True, metavar = 'string', help = 'An ordered, comma separated list of longitudinal attribute ids to add to the data group')

  # Required parameters
  required_arguments.add_argument('--name', '-n', required = False, metavar = 'string', help = 'The name of the data group attribute')

  # Optional parameters
  optional_arguments.add_argument('--description', '-d', required = False, metavar = 'string', help = 'The description of the data group attribute')
  optional_arguments.add_argument('--is_public', '-u', required = False, action = 'store_true', help = 'Set to make the data group attribute public')
  optional_arguments.add_argument('--is_editable', '-e', required = False, action = 'store_true', help = 'Set to make the data group attribute editable')

  return parser.parse_args()

if __name__ == "__main__":
  main()
