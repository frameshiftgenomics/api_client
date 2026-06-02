import argparse
import os
import json

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
  api_store  = Store(config_file = args.client_config)
  api_mosaic = Mosaic(config_file = args.client_config)

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # Set the display type
  allowed_display_types = ['time', 'date', 'duration', 'custom', 'badge']
  if args.display_type:
    if args.display_type not in allowed_display_types:
      fail('unknown display type: ' + args.display_type)
    display_type = args.display_type
  else:
    display_type = None

  # Check that the severity is a json
  if args.severity:
    try:
      json.loads(args.severity)
    except Exception as e:
      fail('Severity string is not in json format. Error: ' + str(e))

  # Check that color is a json
  if args.color:
    try:
      color_json = json.loads(args.color)
    except Exception as e:
      fail('Color string is not in json format. Error: ' + str(e))

    # Check if there are already colors associated with the project
    try:
      data = project.get_project_attribute_definitions(attribute_ids=[args.attribute_id])
      if len(data) != 1:
        fail('Got information on more than one attribute')
      existing_colors = data[0]['color']
    except Exception as e:
      fail('failed to get existing colors for the attribute. Error was: ' + str(e))
   
    same_colors = {}
    different_colors = {}
    new_colors = {}
    omitted_colors = {}
    all_colors = {}
    for value in color_json:

      # Check for mututally exlusive flags
      if args.omit_colors and args.add_existing_colors:
        fail('--omit_colors (-oc) and --add_existing_colors (-ac) are mutually exclusive')

      # If the value in the input already exists in the project, check if the color has changed
      if value in existing_colors:
        if existing_colors[value] == color_json[value]:
          same_colors[value] = color_json[value]
          all_colors[value] = color_json[value]
        else:
          different_colors[value] = color_json[value]
          all_colors[value] = color_json[value]
      else:
        new_colors[value] = color_json[value]
        all_colors[value] = color_json[value]

    # Check for existing colors that will have their colors removed
    for value in existing_colors:
      if value not in color_json:
        omitted_colors[value] = existing_colors[value]

    # If colors are to be omitted, the args.omit_colors flag must be set or the omitted values need
    # to be added to the args.color
    if len(omitted_colors) > 0:
      if not args.omit_colors and not args.add_existing_colors:
        print('ERROR: These values will have colors removed. Add these to the json string, or set --omit_colors (-oc) or --add_existing_colors (-ac):')
        for value in omitted_colors:
          print('  ', value, ': ', omitted_colors[value], sep = '')
        exit(1)

      # Add the existing colors
      elif args.add_existing_colors:
        for value in omitted_colors:
          all_colors[value] = omitted_colors[value]
        args.color = json.dumps(all_colors)

  # Get the project settings
  is_editable = 'false' if args.is_editable else 'true'
  only_suggest_predefined = 'true' if args.only_suggest_predefined else 'false'
  values = args.predefined_values.split(',') if args.predefined_values else None
  original_project_id = args.original_project_id if args.original_project_id else None
  try:
    project.put_project_attributes(args.attribute_id, \
                                        description=args.description, 
                                        name=args.name, \
                                        original_project_id=original_project_id, \
                                        only_suggest_predefined_values = only_suggest_predefined, \
                                        predefined_values=values, \
                                        is_editable=is_editable, \
                                        display_type=display_type, \
                                        value=args.value, \
                                        color=args.color, \
                                        severity = args.severity)
  except Exception as e:
    fail('Failed to update the attribute. Error: ' + str(e))

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  api_arguments = parser.add_argument_group('API Arguments')
  project_arguments = parser.add_argument_group('Project Arguments')
  required_arguments = parser.add_argument_group('Required Arguments')
  optional_arguments = parser.add_argument_group('Optional Arguments')
  display_arguments = parser.add_argument_group('Display Information')

  api_arguments.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  api_arguments.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

  # The project id to which the filter is to be added is required
  required_arguments = parser.add_argument_group('Required Arguments')
  required_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')
  required_arguments.add_argument('--attribute_id', '-i', required = True, metavar = 'integer', help = 'The Mosaic attribute id to update')

  # Optional arguments to update
  optional_arguments = parser.add_argument_group('Optional Arguments')
  optional_arguments.add_argument('--name', '-n', required = False, metavar = 'string', help = 'The name of the attribute')
  optional_arguments.add_argument('--description', '-d', required = False, metavar = 'string', help = 'The attribute description')
  optional_arguments.add_argument('--original_project_id', '-o', required = False, metavar = 'string', help = 'The id of the project that the attribute should live in')
  optional_arguments.add_argument('--display_type', '-dt', required = False, metavar = 'string', help = 'The display type for the attribute: badge, time, date, duration, custom')
  optional_arguments.add_argument('--is_editable', '-e', required = False, action = 'store_true', help = 'If set, the attribute will not be editable')
  optional_arguments.add_argument('--only_suggest_predefined', '-os', required = False, action = 'store_true', help = 'If set, when editing the attribute, only predefined values will be suggested')
  optional_arguments.add_argument('--predefined_values', '-r', required = False, metavar = 'string', help = 'A comma separated list of values that will be available by default')
  optional_arguments.add_argument('--value', '-v', required = False, metavar = 'string', help = 'The value of the attribute')
  optional_arguments.add_argument('--severity', '-se', required = False, metavar = 'string', help = 'A json object of severity levels')
  optional_arguments.add_argument('--color', '-sc', required = False, metavar = 'string', help = 'A json object of colors to use')
  optional_arguments.add_argument('--omit_colors', '-oc', required = False, action = 'store_true', help = 'If colors are included and existing colors are not given a value in the entered json string, those colors will be removed from the attribute. Set this argument if omitting colors is desired, otherwise the update will not proceed')
  optional_arguments.add_argument('--add_existing_colors', '-ac', required = False, action = 'store_true', help = 'If colors are included and existing colors are not given a value in the entered json string, set this flag to keep all existing colors')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
