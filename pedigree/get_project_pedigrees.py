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

  # Open the project
  try:
    project = api_mosaic.get_project(args.project_id)
  except Exception as e:
    fail('failed to open project. Error was: ' + str(e))

  # Get the pedigrees
  try:
    for pedigree in project.get_project_pedigrees():
      if args.only_show_kindred_names:
        print(pedigree['kindred_name'])
      else:
        print(pedigree)
  except Exception as e:
    fail('failed to get pedigrees. Error was: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  display_arguments = groups.display

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to add variant filters to')

  # Only show the kindred names
  display_arguments.add_argument('--only_show_kindred_names', '-on', required = False, action = 'store_true', help = 'Only show the names of the pedigrees')

  return parser.parse_args()

if __name__ == "__main__":
  main()
