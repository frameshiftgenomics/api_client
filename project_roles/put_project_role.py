import json
import os
import sys

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

  # Update the project roles
  try:
    project.put_project_role(args.user_id, args.role_id, args.role_type_id, can_download=None, can_launch_app=None, policy_ids=None)
  except Exception as e:
    fail('Failed to update role. Error was: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required

  # Required arguments
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'string', help = 'The id of the Mosaic project')

  # Required arguments
  required_arguments.add_argument('--user_id', '-u', required = True, metavar = 'string', help = 'The id of the user to update')
  required_arguments.add_argument('--role_id', '-r', required = True, metavar = 'string', help = 'The role id of the user to update')
  required_arguments.add_argument('--role_type_id', '-i', required = True, metavar = 'string', help = 'The id of the role to update the user to. 2: Owner, 3: Admin, 4: Member, 5: Viewer, 6: Technical Staff')

  return parser.parse_args()

if __name__ == "__main__":
  main()
