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

  # The role id is the id of the role record in this project, not a user id or role type id. The
  # server returns a bare 404 for any other id, so check it first and list the project's roles
  try:
    roles = project.get_roles()
  except Exception as e:
    fail('Failed to get the roles for project ' + str(args.project_id) + '. Error was: ' + str(e))
  if int(args.role_id) not in [int(role['id']) for role in roles]:
    message = 'Role id ' + str(args.role_id) + ' is not a role in project ' + str(args.project_id) + '. The project roles are (role id: user id):'
    for role in roles:
      message += '\n  ' + str(role['id']) + ': ' + str(role['user_id'])
    fail(message + '\nTo remove a user by user id or email, use project_roles/delete_project_user.py')

  # Delete the role. For a collection, this also removes the user from the sub-projects unless
  # --disable_cascade is set
  data = project.delete_role(args.role_id, disable_cascade = args.disable_cascade)

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # The role id to delete
  parser.add_argument('--role_id', '-r', required = True, metavar = 'integer', help = 'The role id to delete')

  # For a collection, only remove the role from the collection itself
  parser.add_argument('--disable_cascade', '-dc', required = False, action = 'store_true', help = 'Only remove the role from this project, not from the projects in a collection')

  return parser.parse_args()

if __name__ == "__main__":
  main()
