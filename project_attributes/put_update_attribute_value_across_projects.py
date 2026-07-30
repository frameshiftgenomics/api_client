import os
import sys
import time

from datetime import date
from datetime import datetime
from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():
  global project_info
  global stats

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Open an api client project object for the defined project
  collection = api_mosaic.get_project(args.project_id)
  if not collection.get_project()['is_collection']:
    fail('Supplied project id is not for a collection as required for this script')

  # The same project can have multiple values, so keep track of which projects have already been seen
  observed_projects = []

  # Loop over the attributes and populate project_info with all required project attribute values
  for attribute in collection.get_project_attributes():
    if attribute['id'] == int(args.attribute_id):
      predefined_values = attribute['predefined_values']

      # Check that the attribute value to change to is in the predefined values, or that the new value should
      # be added to the predefined values
      if args.change_value_to not in predefined_values and not args.ignore_predefined_values:
        fail('The value to change to is not in the predefined values')

      # Loop over the attribute values and check if they are in the predefined values
      for value_info in attribute['values']:
        if value_info['value'] == args.change_value_from:

          # Open the relevant project and change the value
          try:
            project = api_mosaic.get_project(value_info['project_id'])
          except Exception as e:
            fail('Could not open project with id ' + str(value_info['project_id']))

          for project_attribute in project.get_project_attributes():
            if project_attribute['id'] == int(args.attribute_id):

              # If this is a longitudinal attribute, a different route is required.
              if project_attribute['is_longitudinal']:
                for existing_value_info in project_attribute['values']:
                  record_date = existing_value_info['record_date'] if existing_value_info['record_date'] else str(datetime.now()).split(' ')[0]
                  value = existing_value_info['value']
                  try:
                    project.put_update_attribute_value(args.attribute_id, existing_value_info['id'], value = args.change_value_to, record_date = record_date)
                  except Exception as e:
                    fail('Failed to update project attribute for project ' + str(value_info['project_id']) + '. Error was: ' + str(e))
              else:
                try:
                  project.put_project_attributes(args.attribute_id, value = args.change_value_to)
                except Exception as e:
                  fail('Failed to update project attribute for project ' + str(value_info['project_id']) + '. Error was: ' + str(e))
      break

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required
  optional_arguments = groups.optional

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # The attribute id to check
  project_arguments.add_argument('--attribute_id', '-i', required = True, metavar = 'integer', help = 'The Mosaic attribute id to edit values for')

  # The attribute value to change from and to
  required_arguments.add_argument('--change_value_from', '-cf', required = True, metavar = 'string', help = 'The attribute value to be changed')
  required_arguments.add_argument('--change_value_to', '-ct', required = True, metavar = 'string', help = 'The attribute value to change to')

  # Choose to add the new value to the predefined values
  optional_arguments.add_argument('--ignore_predefined_values', '-ip', required = False, action = 'store_true', help = 'If set, the new value does not need to be a predefined value')

  return parser.parse_args()

if __name__ == "__main__":
  main()
