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
  try:
    project = api_mosaic.get_project(args.project_id)
  except Exception as e:
    fail('Failed to open project. Error was: ' + str(e))

  # The -dn and -dr options are mutually exclusive
  if args.display_all and args.display_user_id_and_type_id:
    fail('The -dn and -dr options are mutually exclusive')

  # If using a verbose output, get the role types
  if args.display_all:
    role_type_ids = {}
    for role_type in api_mosaic.get_role_types():
      role_type_ids[role_type['id']] = role_type['display_name']

  # Get the roles
  for user in project.get_roles(include_sub_project_roles = args.include_sub_project_roles):
    display = True if (args.user_id and int(args.user_id) == int(user['user_id'])) or not args.user_id else False
    if display:
      if args.display_all:
        print('Role id: ', user['id'], sep = '')
        print('  user_id: ', user['user_id'], sep = '')
        print('  can_download: ', user['can_download'], sep = '')
        print('  can_launch_app: ', user['can_launch_app'], sep = '')
        print('  role_type: ', role_type_ids[user['role_type_id']], ' (id: ', user['role_type_id'], ')', sep = '')
      elif args.display_user_id_and_type_id:
        print(user['user_id'], user['role_type_id'], sep = '\t')
      else:
        print(user['user_id'])

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  display_arguments = groups.display

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id')

  # Optional arguments
  project_arguments.add_argument('--include_sub_project_roles', '-i', required = False, action = 'store_true', help = 'Return roles for projects in a collection')
  project_arguments.add_argument('--user_id', '-u', required = False, metavar = 'integer', help = 'The user id to return roles for')

  # Output
  display_arguments.add_argument('--display_all', '-da', required = False, action = 'store_true', help = 'If set, details of the role will be provided')
  display_arguments.add_argument('--display_user_id_and_type_id', '-dr', required = False, action = 'store_true', help = 'If set, details of the role will be provided')

  return parser.parse_args()

if __name__ == "__main__":
  main()
