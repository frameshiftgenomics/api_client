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

  # Get the project settings
  for attribute in project.get_project_interval_attributes():
    print(attribute['name'], ', ', attribute['id'], sep = '')

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # Verbose output
  parser.add_argument('--verbose', '-v', required = False, action = 'store_true', help = 'Provide a verbose output')

  return parser.parse_args()

if __name__ == "__main__":
  main()
