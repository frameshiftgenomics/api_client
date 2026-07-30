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

  # Get the roles
  for user in project.get_roles():
    if int(args.user_id) == int(user['user_id']):
      print(user['id'])

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id')

  # The id of the user to get the role id for
  project_arguments.add_argument('--user_id', '-u', required = True, metavar = 'integer', help = 'The user id to return roles for')

  return parser.parse_args()

if __name__ == "__main__":
  main()
