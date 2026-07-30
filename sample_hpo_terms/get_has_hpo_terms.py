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
  try:
    print(project.get_has_hpo_terms()['result'])
  except Exception as e:
    fail('failed to get hpo term status. Error was: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  display_arguments = groups.display

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # Output ids only
  display_arguments.add_argument('--ids_only', '-io', required = False, action = 'store_true', help = 'Only output sample ids')
  display_arguments.add_argument('--names_only', '-no', required = False, action = 'store_true', help = 'Only output sample names')

  return parser.parse_args()

if __name__ == "__main__":
  main()
