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
  try:
    project = api_mosaic.get_project(args.project_id)
  except Exception as e:
    fail('Failed to open project. Error was: ' + str(e))

  # Ensure that this is not a collection:
  if project.get_project()['is_collection']:
    fail('This script is only valid for projects and not collections')

  # Loop over all the sample attributes to find that with uid "Relation'. Check if the proband and
  # parents are present
  has_proband = False
  has_mother = False
  has_father = False
  for attribute in project.get_sample_attributes(include_values = 'true'):
    if attribute['uid'] == 'relation':
      for value_info in attribute['values']:
        if value_info['value'] == 'Proband':
          has_proband = True
        elif value_info['value'] == 'Mother':
          has_mother = True
        elif value_info['value'] == 'Father':
          has_father = True

  # Output true if this is a trio, otherwise false
  if has_proband and has_mother and has_father:
    print('true')
  else:
    print('false')

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project

  # The id of the project
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'string', help = 'The id of the project')

  return parser.parse_args()

if __name__ == "__main__":
  main()
