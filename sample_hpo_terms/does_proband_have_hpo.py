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

  # Ensure that this is not a collection:
  if project.get_project()['is_collection']:
    fail('This script is only valid for projects and not collections')

  # Get all the project samples and find the proband
  proband_id = False
  for attribute in project.get_sample_attributes(include_values = 'true'):
    if attribute['uid'] == 'relation':
      for value_info in attribute['values']:
        if value_info['value'] == 'Proband':
          proband_id = value_info['sample_id']
          break

  # Fail if there is no proband
  if not proband_id:
    fail('Project has no sample identified as the proband')

  # Check if the proband has any HPO terms
  if len(project.get_sample_hpo_terms(proband_id)) > 0:
    print('true')
  else:
    print('false')

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project

  # Get the id of the project and the sample whose HPO terms are required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The project id')

  return parser.parse_args()

if __name__ == "__main__":
  main()
