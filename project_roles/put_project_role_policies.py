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

  # Get the role_id for the user
  role_id = False
  for user in project.get_roles()['data']:
    if int(user['user_id']) == int(args.user_id):
      role_id = user['id']
      role_type_id = user['role_type_id']

  # If the user wasn't found, fail
  if not role_id:
    fail('did not find user with id ' + str(args.user_id) + ' in this project')

  # Update the role for this project
  policy_ids = args.policy_ids.split(',') if ',' in args.policy_ids else [args.policy_ids]
  project.put_project_role(role_id, role_type_id, user_id = args.user_id, policy_ids = policy_ids)

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # User ids
  parser.add_argument('--user_id', '-u', required = True, metavar = 'integer', help = 'The user id to assign the policy to')

  # Policy ids
  parser.add_argument('--policy_ids', '-o', required = True, metavar = 'string', help = 'A comma separated list of policy ids to assign to this user')

  return parser.parse_args()

if __name__ == "__main__":
  main()
