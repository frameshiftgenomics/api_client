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
