import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

   # If the api_client path was not specified, get it from the script path
  api_mosaic = init(args)

  # Open an api client project object for the defined project
  try:
    project = api_mosaic.get_project(args.project_id)
  except Exception as e:
    fail('failed to open project. Error was: ' + str(e))

  # Put predefined values into an array
  predefined_values = []
  if args.predefined_values:
    predefined_values = args.predefined_values.split(',')
  only_suggest_predefined_values = 'true' if args.only_suggest_predefined_values else 'false'

  # Import tha annotation
  try:
    project.put_variant_annotation(args.annotation_id, \
                                   name = args.name, \
                                   value_type = args.type, \
                                   privacy_level = args.privacy_level, \
                                   display_type = args.display_type, \
                                   severity = args.severity, \
                                   category = args.category, \
                                   predefined_values = predefined_values, \
                                   only_suggest_predefined_values = only_suggest_predefined_values, \
                                   value_truncate_type = args.value_truncate_type, \
                                   value_max_length = args.value_max_length, \
                                   latest_version_id = args.latest_version_id)
  except Exception as e:
    fail('failed to update annotation. Error was: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required
  optional_arguments = groups.optional

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # The annotation id to update
  required_arguments.add_argument('--annotation_id', '-i', required = True, metavar = 'integer', help = 'The Mosaic annotation id to import')

  # Optional values to update
  optional_arguments.add_argument('--category', '-g', required = False, metavar = 'string', help = 'The category of the annotation')
  optional_arguments.add_argument('--display_type', '-d', required = False, metavar = 'string', help = 'The display type of the annotation')
  optional_arguments.add_argument('--name', '-n', required = False, metavar = 'string', help = 'The name of the annotation')
  optional_arguments.add_argument('--predefined_values', '-pv', required = False, metavar = 'string', help = 'A comma separated list of predefined values')
  optional_arguments.add_argument('--only_suggest_predefined_values', '-opv', required = False, action = 'store_true', help = 'Only suggest predefined values in the dropdown')
  optional_arguments.add_argument('--privacy_level', '-l', required = False, metavar = 'string', help = 'The privacy level of the annotation')
  optional_arguments.add_argument('--severity', '-s', required = False, metavar = 'string', help = 'The severity of the annotation')
  optional_arguments.add_argument('--type', '-t', required = False, metavar = 'string', help = 'The type of the annotation')
  optional_arguments.add_argument('--value_truncate_type', '-v', required = False, metavar = 'string', help = 'The method of truncating the annotation values')
  optional_arguments.add_argument('--value_max_length', '-m', required = False, metavar = 'string', help = 'The max length of the of the annotation values')

  # Set the latest version
  parser.add_argument('--latest_version_id', '-e', required = False, metavar = 'integer', help = 'The annotation version id to set as the latest version')

  return parser.parse_args()

if __name__ == "__main__":
  main()
