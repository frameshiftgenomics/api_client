import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

# Remove a user from a project by deleting their role in it. The user can be identified by id or email

def main():

  # Parse the command line
  args = parse_command_line()

  # Exactly one way of identifying the user must be given
  if bool(args.user_id) == bool(args.email):
    fail('Exactly one of --user_id or --email must be supplied')

  api_mosaic = init(args)

  # Get the user id from the email address if required
  user_id = args.user_id
  if args.email:
    try:
      user_id = api_mosaic.get_user_by_email(args.email)['id']
    except Exception as e:
      fail('Failed to find user with email ' + args.email + '. Error was: ' + str(e))

  # Open an api client project object for the defined project
  try:
    project = api_mosaic.get_project(args.project_id)
  except Exception as e:
    fail('Failed to open project. Error was: ' + str(e))

  # Find the user's role in the project
  role = None
  for project_role in project.get_roles():
    if int(project_role['user_id']) == int(user_id):
      role = project_role
      break
  if not role:
    fail('User ' + str(user_id) + ' does not have a role in project ' + str(args.project_id))

  # Delete the role
  try:
    project.delete_role(role['id'], disable_cascade = args.disable_cascade)
  except Exception as e:
    fail('Failed to remove user from project. Error was: ' + str(e))
  print('Removed user ', user_id, ' from project ', args.project_id, ' (role id: ', role['id'], ')', sep = '')

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  optional_arguments = groups.optional

  # The project id is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to remove the user from')

  # The user to remove, identified by id or email
  project_arguments.add_argument('--user_id', '-u', required = False, metavar = 'integer', help = 'The id of the user to remove')
  project_arguments.add_argument('--email', '-e', required = False, metavar = 'string', help = 'The email address of the user to remove')

  # Optional arguments
  optional_arguments.add_argument('--disable_cascade', '-dc', required = False, action = 'store_true', help = 'Only remove the user from this project, not from the projects in a collection')

  return parser.parse_args()

if __name__ == "__main__":
  main()
