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

  # Get the array of ids to look at
  attribute_ids = False
  if args.attribute_ids:
    attribute_ids = args.attribute_ids.split(',') if ',' in args.attribute_ids else [args.attribute_ids]

  # Get the project settings
  for attribute in project.get_project_attribute_definitions(attribute_ids = attribute_ids):
    display = False if args.attribute_ids else True
    if args.attribute_ids:
      if str(attribute['id']) in attribute_ids:
        display = True

    # Only display if the attribute is requested
    if display:
      if not args.display_all_information:
        print(attribute['name'], ': ', attribute['id'], sep = '')
      else:
        print(attribute['name'], ' (id: ', attribute['id'], ')', sep = '')
        print('   created_at: ', attribute['created_at'], ', updated_at: ', attribute['updated_at'], sep = '')
        for attribute_info in sorted(attribute.keys()):
          if attribute_info == 'name' or attribute_info == 'id':
            continue
          elif attribute_info == 'created_at' or attribute_info == 'updated_at':
            continue
          elif attribute_info == 'predefined_values':
            if len(attribute['predefined_values']) > 0:
              print('   predefined_values:')
              for value in attribute['predefined_values']:
                print('      ', value, sep = '')
            else:
              print('   predefined values: none set')
          elif attribute_info == 'start_attribute_id':
            print('   start attribute id: ', attribute['start_attribute_id'], ', end attribute id: ', attribute['end_attribute_id'], sep = '')
          elif attribute_info == 'end_attribute_id':
            continue
          elif attribute_info == 'values':
            if args.include_values:
              print('   values:')
              for value in attribute['values']:
                print('      ', value['value'], ': ', value['id'])
          else:
            print('   ', attribute_info, ': ', attribute[attribute_info], sep = '')

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  display_arguments = groups.display

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')
  project_arguments.add_argument('--attribute_ids', '-i', required = False, metavar = 'string', help = 'A comma separated list of attribute ids to view. If omitted, all will be shown')

  # Include values
  display_arguments.add_argument('--include_values', '-v', required = False, action = 'store_true', help = 'Include attribute values in the output. Only output when used in conjunction with --verbose')

  # Verbose output
  display_arguments.add_argument('--display_all_information', '-da', required = False, action = 'store_true', help = 'Display Provide a verbose output')

  return parser.parse_args()

if __name__ == "__main__":
  main()
