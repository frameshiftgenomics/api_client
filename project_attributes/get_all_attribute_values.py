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
  try:
    project = api_mosaic.get_project(args.project_id)
  except Exception as e:
    fail('Failed to open project. Error was: ' + str(e))

  # Loop over the required attributes and get the required information about them
  for attribute in project.get_project_attribute_definitions(attribute_ids = [args.attribute_id]):
    values = []
    predefined_values = attribute['predefined_values']

    # Loop over all of the values and find all unique values
    for value in project.get_unique_project_attribute_values(args.attribute_id):
      if value not in values and value:

          # If the display_non_predefined flag is set, only store the value if it is not
          # a predefined value
          if value not in predefined_values or not args.display_non_predefined:
            values.append(value) 

  # Print out the values
  for value in sorted(values):
    print('\'', value, '\'', sep = '')

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  display_arguments = groups.display

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')
  project_arguments.add_argument('--attribute_id', '-i', required = True, metavar = 'integer', help = 'The id of the attribute to view')

  # Verbose output
  display_arguments.add_argument('--display_non_predefined', '-dn', required = False, action = 'store_true', help = 'Only display values that are not in the predefined values list')

  return parser.parse_args()

if __name__ == "__main__":
  main()
