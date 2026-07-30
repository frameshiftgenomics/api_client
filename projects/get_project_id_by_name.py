import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():
  global allowed_references
  global system_projects

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Get all the available projects
  project_id = False
  for project_info in api_mosaic.get_projects():

    # Check if the project name is the same as defined on the command line
    if str(project_info['name']) == str(args.project_name):
      project_id = project_info['id']
      break

  # Write out the project id
  if not project_id:
    print('No project found with the given name')
  else:
    print(project_id)

# Input options
def parse_command_line():
  parser, groups = base_parser()
  required_arguments = groups.required

  # Get the name of the project to get the id for
  required_arguments.add_argument('--project_name', '-p', required = True, metavar = 'string', help = 'The name of the project to find the id of')

  return parser.parse_args()

if __name__ == "__main__":
  main()
