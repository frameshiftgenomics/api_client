import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Loop over all projects, then all users (roles) in the project
  for project_info in api_mosaic.get_projects():
    project = api_mosaic.get_project(project_info['id'])
    for role in project.get_roles()['data']:

      # Do not delete owners or super admins
      if role['role_type_id'] != 1 and role['role_type_id'] != 2:

        # Delete the role
        data = project.delete_role(role['id'])

# Input options
def parse_command_line():
  parser, _ = base_parser()

  return parser.parse_args()

if __name__ == "__main__":
  main()
