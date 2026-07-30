import os
import sys
import json

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # Get the project settings
  is_editable = 'false' if args.is_editable else 'true'
  if args.is_public == 'public':
    is_public = 'true'
  elif args.is_public == 'private':
    is_public = 'false'
  else: 
    fail('is_public must be "public" or "private"')

  # Check the attribute type
  if args.value_type != 'float' and args.value_type != 'string' and args.value_type != 'timestamp':
    fail('value_type must be "float" or "string", or "timestamp"')

  # Set the predefined values
  predefined_values = args.predefined_values.split(',') if args.predefined_values else None

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
      json.loads(args.color)
    except Exception as e:
      fail('Color string is not in json format. Error: ' + str(e))

  # Deal with whether the attribute is editable or longitudinal
  is_editable = 'false' if args.is_editable else 'true'
  is_longitudinal = 'true' if args.is_longitudinal else 'false'
  only_suggest_predefined = 'true' if args.only_suggest_predefined else 'false'

  # Create the attribute
  try:
    project.post_project_attribute(description = args.description, \
                                   name = args.name, \
                                   predefined_values = predefined_values, \
                                   value = args.value, \
                                   value_type = args.value_type, \
                                   is_editable = is_editable, \
                                   is_longitudinal = is_longitudinal, \
                                   is_public = is_public, \
                                   display_type = display_type, \
                                   severity = args.severity, \
                                   color = args.color, \
                                   only_suggest_predefined_values = only_suggest_predefined)
  except Exception as e:
    fail('Failed to create attribute. Error was: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required
  optional_arguments = groups.optional

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # Required arguments for creating a new attribute
  required_arguments.add_argument('--name', '-n', required = True, metavar = 'string', help = 'The name of the attribute')
  required_arguments.add_argument('--is_public', '-u', required = True, metavar = 'string', help = 'Is the project "public" or "private"')
  required_arguments.add_argument('--value_type', '-t', required = True, metavar = 'string', help = 'The value type must be "float", "string", or "timestamp"')

  # Optional arguments to update
  optional_arguments.add_argument('--description', '-d', required = False, metavar = 'string', help = 'The attribute description')
  optional_arguments.add_argument('--is_editable', '-e', required = False, action = 'store_true', help = 'If set, the attribute will not be editable')
  optional_arguments.add_argument('--is_longitudinal', '-l', required = False, action = 'store_true', help = 'If set, the attribute will not longitudinal')
  optional_arguments.add_argument('--only_suggest_predefined', '-o', required = False, action = 'store_true', help = 'If set, when editing the attribute, only predefined values will be suggested')
  optional_arguments.add_argument('--predefined_values', '-r', required = False, metavar = 'string', help = 'A comma separated list of values that will be available by default')
  optional_arguments.add_argument('--value', '-v', required = False, metavar = 'string', help = 'The value of the attribute')
  optional_arguments.add_argument('--display_type', '-dt', required = False, metavar = 'string', help = 'The display type for the attribute: badge, time, date, duration, custom')
  optional_arguments.add_argument('--severity', '-se', required = False, metavar = 'string', help = 'A json object of severity levels')
  optional_arguments.add_argument('--color', '-sc', required = False, metavar = 'string', help = 'A json object of colors to use')

  return parser.parse_args()

if __name__ == "__main__":
  main()
