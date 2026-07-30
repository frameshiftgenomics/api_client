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

  # Check if this is a collection
  data = project.get_project()
  if data['is_collection']:
    project_ids = data['collection_project_ids']
  else:
    project_ids = [args.project_id]

  # Loop over all the projects
  for project_id in project_ids:
    print('Deleting experiments from project ', project_id, sep = '')
    project = api_mosaic.get_project(project_id)
    for experiment in project.get_experiments():
      project.delete_experiment(experiment['id'])

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The project id
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id')

  return parser.parse_args()

if __name__ == "__main__":
  main()
