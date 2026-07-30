import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # Delete the user project settings
  project.delete_user_project_settings()

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The id of the attribute form to delete
  parser.add_argument('--project_id', '-p', required = True, metavar = 'string', help = 'The id of the project to delete')

  return parser.parse_args()

if __name__ == "__main__":
  main()
