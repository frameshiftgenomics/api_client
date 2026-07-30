import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Create the project object
  project = api_mosaic.get_project(args.project_id)

  # Chekc the resource_type
  allowed_types = ['project_attribute',
                   'project_conversation']
  resource_type = args.resource_type if args.resource_type in allowed_types else fail('Unknown resource type')

  # Get the attributse
  for attribute in project.get_policy_project_resources(resource_type):
    print(attribute)

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to get policy attributes for')

  # Optional resource type to get
  parser.add_argument('--resource_type', '-t', required = True, metavar = 'string', help = 'The resource type to return: project_attribute, project_conversation')

  return parser.parse_args()

if __name__ == "__main__":
  main()
