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
  try:
    project = api_mosaic.get_project(args.project_id)
  except Exception as e:
    fail('Failed to open project. Error was: ' + str(e))

  # Check the value-type is allowed
  allowed_types = ['float', 'string']
  if args.value_type not in allowed_types:
    fail('the type must be one of the following: ' + ', '.join(allowed_types))

  # Get the type of the requested attribute
  for attribute in project.get_project_attribute_definitions(attribute_ids = [args.attribute_id]):
    value_type = attribute['value_type']
  if str(value_type) == args.value_type:
    fail('the requested value type is the current value type. No change is required')

  # Update the attribute
  try:
    project.put_convert_project_attribute_type(args.attribute_id, args.value_type)
  except Exception as e:
    fail('Failed to convert the attribute. Error was: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required

  # The project id
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # The attribute id and the new type are required
  required_arguments.add_argument('--attribute_id', '-i', required = True, metavar = 'integer', help = 'The Mosaic attribute id to update')
  required_arguments.add_argument('--value_type', '-v', required = True, metavar = 'string', help = 'The new type to apply to the attribute. The allowed types are: float, string')

  return parser.parse_args()

if __name__ == "__main__":
  main()
