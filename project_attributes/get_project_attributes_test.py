import argparse
import os
import sys

from pprint import pprint
from sys import path

def main():

  # Common code for all scripts living in the api client directories. This will get the mosaic
  # endpoints and initialise the argument parsing
  sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
  from _bootstrap import init, base_parser, warning, fail
  args = set_command_line_arguments(base_parser())
  api_mosaic, api_store = init(args)

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # Get the array of ids to look at
  attribute_ids = False
  if args.attribute_ids:
    attribute_ids = args.attribute_ids.split(',') if ',' in args.attribute_ids else [args.attribute_ids]

  # Get the project settings
  for attribute in project.get_project_attributes():
    display = False if args.attribute_ids else True
    if args.attribute_ids:
      if str(attribute['id']) in attribute_ids:
        display = True

    # Only display if the attribute is requested
    if display:
      if not args.display_all_information:
        print(attribute['name'], ': ', attribute['id'], sep = '')
        if args.include_values:
          print('   values:')
          for value in attribute['values']:
            print('      project_id: ', value['project_id'], ', value_id: ', value['id'], ', value: ', value['value'], sep = '')
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
                print('      project_id: ', value['project_id'], ', value_id: ', value['id'], ', value: ', value['value'], sep = '')
          else:
            print('   ', attribute_info, ': ', attribute[attribute_info], sep = '')

# Input options
def set_command_line_arguments(parser):
  groups = {g.title: g for g in parser._action_groups}
  groups['project arguments'].add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id')
  groups['project arguments'].add_argument('--attribute_ids', '-i', required = False, metavar = 'string', help = 'A comma separated list of attribute ids to view. If omitted, all will be shown')
  groups['display arguments'].add_argument('--include_values', '-v', required = False, action = 'store_true', help = 'Include attribute values in the output. Only output when used in conjunction with --verbose')
  groups['display arguments'].add_argument('--display_all_information', '-da', required = False, action = 'store_true', help = 'Display Provide a verbose output')

  return parser.parse_args()

if __name__ == "__main__":
  main()
