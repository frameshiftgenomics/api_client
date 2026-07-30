import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line and open the Mosaic endpoints
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
  for attribute in project.get_project_attributes():
    display = False if args.attribute_ids else True
    if args.attribute_ids:
      if str(attribute['id']) in attribute_ids:
        display = True

    # If attributes with a single predefined value are required
    if args.find_single_predefined_value_with_comma:
      if not (len(attribute['predefined_values']) == 1 and ',' in attribute['predefined_values'][0]):
        display = False

    # Only display longitudinal attribute if requested
    if args.only_longitudinal and not attribute['is_longitudinal']:
      display = False

    # If we only want attributes that are members of a data group
    if args.in_data_groups and len(attribute['data_groups']) == 0:
      display = False

    # Only display if the attribute is requested
    if display:
      if args.ids_only:
        print(attribute['id'])
      elif args.list_data_groups:
        data_groups = []
        for data_group in attribute['data_groups']:
          data_groups.append(data_group['name'])
        if args.display_name_not_id:
          print(attribute['name'], ': ', ', '.join(data_groups), sep = '')
        else:
          print(attribute['id'], ': ', ', '.join(data_groups), sep = '')
      elif not args.display_all_information:
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
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  display_arguments = groups.display

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')
  project_arguments.add_argument('--attribute_ids', '-i', required = False, metavar = 'string', help = 'A comma separated list of attribute ids to view. If omitted, all will be shown')

  # Include values
  display_arguments.add_argument('--include_values', '-v', required = False, action = 'store_true', help = 'Include attribute values in the output')

  # Verbose output
  display_arguments.add_argument('--display_all_information', '-da', required = False, action = 'store_true', help = 'Display Provide a verbose output')

  # Only display longitudinal attributes
  display_arguments.add_argument('--only_longitudinal', '-ol', required = False, action = 'store_true', help = 'Only display longitudinal attributes')

  # Only display longitudinal attributes that are in data groups and allow these to be listed
  display_arguments.add_argument('--in_data_groups', '-dg', required = False, action = 'store_true', help = 'If set, only show attributes that are part of a data group')
  display_arguments.add_argument('--list_data_groups', '-ldg', required = False, action = 'store_true', help = 'If set, output the data groups the attributes are members of')
  display_arguments.add_argument('--display_name_not_id', '-dn', required = False, action = 'store_true', help = 'If set, output the attribute name instead of the id')

  # Only display longitudinal attributes that are part of these data groups
  display_arguments.add_argument('--ids_only', '-io', required = False, action = 'store_true', help = 'If set, only output the attribute ids')

  # Find attributes with a single predefined value that contains a comma (e.g. cases where
  # user accidentally added a single value instead of multiple values)
  display_arguments.add_argument('--find_single_predefined_value_with_comma', '-pc', required = False, action = 'store_true', help = 'Output attributes with a single predefined value that also contains a comma')

  return parser.parse_args()

if __name__ == "__main__":
  main()
