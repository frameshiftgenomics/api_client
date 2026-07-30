import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Get the attributes ids into a list
  attribute_ids = None
  if args.attribute_ids:
    attribute_ids = args.attribute_ids.split(',') if ',' in args.attribute_ids else [int(args.attribute_ids)]

  # Get the attributes available for import
  for attribute in api_mosaic.get_public_project_attributes(attribute_ids = attribute_ids):
    if not args.display_all_information: 
      print(attribute['name'], ': ', attribute['id'], sep = '') 
    else: 
      print(attribute['name'], ' (id: ', attribute['id'], ')', sep = '') 
      if attribute['description']: 
        print('  description: ', attribute['description'], sep = '') 
      print('    uid: ', attribute['uid'], sep = '') 
      print('    value_type: ', attribute['value_type'], sep = '') 
      print('    original_project_id: ', attribute['original_project_id'], sep = '') 
      print('    is_custom: ', attribute['is_custom'], sep = '') 
      print('    is_editable: ', attribute['is_editable'], sep = '') 
      print('    is_longitudinal: ', attribute['is_longitudinal'], sep = '') 
      print('    is_public: ', attribute['is_public'], sep = '') 
      print('    custom_display_format: ', attribute['custom_display_format'], sep = '') 
      print('    display_type: ', attribute['display_type'], sep = '') 
      if attribute['predefined_values']: 
        print('    predefined_values:') 
        for value in attribute['predefined_values']: 
          print('      ', value, sep = '') 
      if attribute['source']: 
        print('    source: ', attribute['source'], sep = '') 
      if attribute['start_attribute_id']: 
        print('    Start id: ', attribute['start_attribute_id'], ', End id: ', attribute['end_attribute_id'], sep = '') 
      print('    created_at: ', attribute['created_at'], ', updated_at: ', attribute['updated_at'], sep = '') 

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  display_arguments = groups.display

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--attribute_ids', '-i', required = False, metavar = 'string', help = 'A comma separated list of attribute ids to view. If omitted, all will be shown')

  # Verbose output
  display_arguments.add_argument('--display_all_information', '-da', required = False, action = 'store_true', help = 'Display Provide a verbose output')

  return parser.parse_args()

if __name__ == "__main__":
  main()
