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

  # Determine whether to show values
  include_values = 'true' if args.include_values else 'false'

  # Make sure the attribute ids are a list
  attribute_ids = None
  if args.attribute_ids:
    attribute_ids = args.attribute_ids.split(',') if ',' in args.attribute_ids else [args.attribute_ids]

  # Get the attributes for the sample
  for attribute in project.get_sample_attributes(attribute_ids = attribute_ids, include_values = include_values):
    if args.only_show_values and include_values:
      for value in attribute['values']:
        print(value['value'])
    elif include_values:
      print(attribute['id'], ': ', attribute['name'], sep = '')
      if 'values' in attribute:
        for value in attribute['values']:
          print('  sample: ', value['sample_id'], ', value: ', value['value'], sep = '')
    else:
      pprint(attribute)

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  optional_arguments = groups.optional

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # The sample id to get attributes for
  optional_arguments.add_argument('--attribute_ids', '-t', required = False, metavar = 'integer', help = 'A comma separated list of attribute ids')
  optional_arguments.add_argument('--include_values', '-v', required = False, action = 'store_true', help = 'Set to output values for all samples')
  optional_arguments.add_argument('--only_show_values', '-ov', required = False, action = 'store_true', help = 'Only show the values for the selected attributes')

  return parser.parse_args()

if __name__ == "__main__":
  main()
