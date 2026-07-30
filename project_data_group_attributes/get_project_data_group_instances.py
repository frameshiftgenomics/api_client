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
  project = api_mosaic.get_project(args.project_id)

  # Get all attributes in the project. When looping over data group attributes, this is needed to get the names
  # of the data group attributes
  project_attributes = {}
  for attribute in project.get_project_attributes():
    project_attributes[attribute['id']] = attribute['name']

  # Get all data group attributes
  for data_group_instance in project.get_data_group_instances(args.attribute_id):
    print('instance id: ', data_group_instance['id'], sep = '')

    # Format the time stringds
    format_string = "%Y-%m-%dT%H:%M:%S.%fZ"
    record_date = str(datetime.strptime(data_group_instance['record_date'], format_string)).split('.')[0]
    created_at = str(datetime.strptime(data_group_instance['created_at'], format_string)).split('.')[0]
    updated_at = str(datetime.strptime(data_group_instance['updated_at'], format_string)).split('.')[0]
    if args.display_all_information:
      print('  record date: ', record_date, sep = '')
      print('  created_at: ', created_at, ', updated_at: ', updated_at, sep = '')
    for attribute in data_group_instance['data_group_attribute_values']:
      if args.display_all_information:
        print('  attribute id: ', attribute['attribute_id'], ', id: ', attribute['id'], sep = '')
        record_date = str(attribute['record_date']).split('+')[0]
        record_date = str(datetime.strptime(record_date, format_string)).split('.')[0]
        print('    record_date: ', record_date, sep = '')
        print('    custom_display_format: ', attribute['custom_display_format'], sep = '')
        print('    display_type: ', attribute['display_type'], sep = '')
        print('    value_type: ', attribute['value_type'], sep = '')
        print('    value: ', attribute['value'], sep = '')
      else:
        print('  attribute id: ', attribute['attribute_id'], ', id: ', attribute['id'], ', value: ', attribute['value'], sep = '')

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  display_arguments = groups.display

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')
  project_arguments.add_argument('--attribute_id', '-i', required = True, metavar = 'integer', help = 'The Mosaic id of the data group attribute')

  # Optional viewing options
  display_arguments.add_argument('--display_all_information', '-da', required = False, action = 'store_true', help = 'Include all data group information')

  return parser.parse_args()

if __name__ == "__main__":
  main()
