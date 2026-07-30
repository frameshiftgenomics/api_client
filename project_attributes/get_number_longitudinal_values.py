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

  # Find the attribute
  project_value_counts = {}
  for attribute in project.get_project_attributes():
    if attribute['id'] == int(args.attribute_id):

      # Loop over all of the values and find all unique values
      for value_info in attribute['values']:
        if value_info['project_id'] not in project_value_counts:
          project_value_counts[value_info['project_id']] = 1
        else:
          project_value_counts[value_info['project_id']] += 1

  # Write out the results
  output_list = []
  for project_id in sorted(project_value_counts):
    number_values = project_value_counts[project_id]
    if number_values > 1 or not args.display_multivalued:
      if args.output_comma_separated_list:
        output_list.append(str(project_id))
      else:
        print(project_id, ':\t', project_value_counts[project_id], sep = '')

  # Output the comma separated list
  if args.output_comma_separated_list and len(output_list) > 0:
    print(','.join(output_list))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  display_arguments = groups.display

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')
  project_arguments.add_argument('--attribute_id', '-i', required = True, metavar = 'integer', help = 'The attribute id to view')

  # Only display projects with multiple values
  display_arguments.add_argument('--display_multivalued', '-dm', required = False, action = 'store_true', help = 'Only show projects with multiple values for the attribute')
  display_arguments.add_argument('--output_comma_separated_list', '-ol', required = False, action = 'store_true', help = 'Output a comma separated list of project ids')

  return parser.parse_args()

if __name__ == "__main__":
  main()
