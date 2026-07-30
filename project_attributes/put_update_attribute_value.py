import os
import sys
import json

from datetime import datetime
from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # If the record date is not supplied, use todays date
  args.record_date = str(datetime.now()).split(' ')[0] if not args.record_date else args.record_date

  try:
    project.put_update_attribute_value(args.attribute_id, args.value_id, value = args.value, record_date = args.record_date)
  except Exception as e:
    fail('Failed to update the attribute value. Error: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required
  optional_arguments = groups.optional

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # Information about the attribute
  required_arguments.add_argument('--attribute_id', '-i', required = True, metavar = 'integer', help = 'The Mosaic attribute id to update')
  required_arguments.add_argument('--value_id', '-v', required = True, metavar = 'integer', help = 'The Mosaic value id to update')

  # If the value is left blank, it will be set to null
  optional_arguments.add_argument('--value', '-va', required = False, metavar = 'string', help = 'The value of the attribute')

  # Optional arguments to update
  optional_arguments.add_argument('--record_date', '-r', required = False, metavar = 'string', help = 'The date to update the value record date to')

  return parser.parse_args()

if __name__ == "__main__":
  main()
