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

  # Get all attributes in the project. When looping over data group attributes, this is needed to get the names
  # of the data group attributes
  project_attributes = {}
  for attribute in project.get_project_attributes():
    project_attributes[attribute['id']] = attribute['name']

  # If attribute ids were provided, put them in a list
  attribute_ids = []
  if args.attribute_ids:
    attribute_ids = [int(item) for item in args.attribute_ids.split(',')]

  # Get all data group attributes
  for data_group in project.get_project_data_group_attributes(filter_restricted_project_id=None):

    # Only show requested attributes
    if (args.attribute_ids and data_group['id'] in attribute_ids) or not args.attribute_ids:
      print(data_group['name'], ': ', data_group['id'], sep = '')
      if args.display_all_information:
        print('  uid: ', data_group['uid'], sep = '')
        print('  description: ', data_group['description'], sep = '')
        print('  original project id: ', data_group['original_project_id'], sep = '')
        print('  is custom: ', data_group['is_custom'], sep = '')
        print('  is editable: ', data_group['is_editable'], sep = '')
        print('  is public: ', data_group['is_public'], sep = '')
        print('  instance count: ', data_group['instances_count'], sep = '')
  
        # Format the time stringds
        format_string = "%Y-%m-%dT%H:%M:%S.%fZ"
        created_at = str(datetime.strptime(data_group['created_at'], format_string)).split('.')[0]
        updated_at = str(datetime.strptime(data_group['updated_at'], format_string)).split('.')[0]
  
        print('  created_at: ', created_at, ', updated_at: ', updated_at, sep = '')
        print('  predefined values: ', data_group['predefined_values'], sep = '')
      if args.include_attributes:
        print('  included attributes: ')
        for attribute in data_group['data_group_attributes']:
          print('    ', attribute['id'], ': ', project_attributes[attribute['attribute_id']], ': ', attribute['attribute_id'], sep = '')
      if args.output_attribute_id_list:
        id_list = ''
        for attribute in data_group['data_group_attributes']:
          id_list += str(attribute['attribute_id']) + ','
        id_list = id_list.rstrip(',')
        print('  included attribute list: ', id_list, sep = '')

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  optional_arguments = groups.optional
  display_arguments = groups.display

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # Optional arguments
  optional_arguments.add_argument('--attribute_ids', '-ai', required = False, metavar = 'string', help = 'A comma separated list of attribute ids to return information on')

  # Optional viewing options
  display_arguments.add_argument('--include_attributes', '-i', required = False, action = 'store_true', help = 'Include constituent attributes in output')
  display_arguments.add_argument('--display_all_information', '-da', required = False, action = 'store_true', help = 'Include all data group information')
  display_arguments.add_argument('--output_attribute_id_list', '-il', required = False, action = 'store_true', help = 'For each data group, output a comma separated list of the constituent attribute ids')

  return parser.parse_args()

if __name__ == "__main__":
  main()
