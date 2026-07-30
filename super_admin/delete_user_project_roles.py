import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Add the project ids to a list
  project_ids = []
  if ',' in args.project_ids:
    for project_id in args.project_ids.split(','):
      project_ids.append(int(project_id))
  else:
    project_ids.append(int(args.project_ids))

  # Remove the user from the given projects
  api_mosaic.delete_user_project_roles(args.user_id, project_ids = project_ids)

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The user id
  parser.add_argument('--user_id', '-u', required = True, metavar = 'integer', help = 'The id of the user whose roles are to be deleted')

  # The projects to remove the user from
  parser.add_argument('--project_ids', '-p', required = True, metavar = 'string', help = 'A comma separated list of project ids to remove the user from')

  return parser.parse_args()

if __name__ == "__main__":
  main()
