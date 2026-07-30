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
  project = api_mosaic.get_project(args.project_id)

  # Import the attribute
  project.post_import_project_attribute(args.attribute_id, value = args.attribute_value)

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # The attribute id to delete and optionally a value to assign
  parser.add_argument('--attribute_id', '-i', required = True, metavar = 'integer', help = 'The id of the attribute to delete')
  parser.add_argument('--attribute_value', '-v', required = False, metavar = 'string', help = 'The value to assign the attribute')

  return parser.parse_args()

if __name__ == "__main__":
  main()
