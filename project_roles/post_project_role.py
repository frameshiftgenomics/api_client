import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Get the project
  try:
    project = api_mosaic.get_project(args.project_id)
  except Exception as e:
    fail('Couldn\'t open project. Error was: ' + str(e))

  # Update the project roles
  project.post_project_role(args.user_id, args.role_type_id, can_download=None, can_launch_app=None, policy_ids=None, disable_notification = args.disable_notification)

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project

  # Required arguments
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'string', help = 'The id of the Mosaic project')
  project_arguments.add_argument('--user_id', '-u', required = True, metavar = 'string', help = 'The role id of the user to update')
  project_arguments.add_argument('--role_type_id', '-r', required = True, metavar = 'string', help = 'The id role to update the user to. 2: Owner, 3: Admin, 4: Member, 5: Viewer, 6: Technical Staff')

  # Optional arguments
  project_arguments.add_argument('--disable_notification', '-dn', required = False, action = 'store_true', help = 'Do not send a notification when the role is added')

  return parser.parse_args()

if __name__ == "__main__":
  main()
