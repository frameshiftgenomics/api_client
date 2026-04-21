import os
import argparse

from pprint import pprint
from sys import path

def main():

  # Parse the command line
  args = parse_command_line()

  # If the api_client path was not specified, get it from the script path
  if not args.api_client:
    try:
      args.api_client = os.path.dirname(os.path.realpath(__file__)).split('api_client')[0] + str('api_client')
    except:
      fail('Could not get the api_client path from the command. Please specify using --api_client / -a')

  # Import the api client
  path.append(args.api_client)
  try:
    from mosaic import Mosaic, Project, Store
  except:
    fail('Cannot find mosaic. Please set the --api_client / -a argument')
  api_store = Store(config_file = args.client_config)
  api_mosaic = Mosaic(config_file = args.client_config)

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
  parser = argparse.ArgumentParser(description='Process the command line arguments')
  api_arguments = parser.add_argument_group('API Arguments')
  project_arguments = parser.add_argument_group('Project Arguments')
  required_arguments = parser.add_argument_group('Required Arguments')
  optional_arguments = parser.add_argument_group('Optional Arguments')
  display_arguments = parser.add_argument_group('Display Information')

  # Define the location of the api_client and the ini config file
  api_arguments.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  api_arguments.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

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

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
