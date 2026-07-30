import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Delete the attribute form
  project = api_mosaic.get_project(args.project_id)
  data = project.get_project()

  if args.output_name:
    print(data['name'])
  else:
    pprint(data)

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  display_arguments = groups.display

  # The id of the project
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'string', help = 'The id of the project')

  # Display options
  display_arguments.add_argument('--output_name', '-on', required = False, action = 'store_true', help = 'Only out the project name')

  return parser.parse_args()

if __name__ == "__main__":
  main()
