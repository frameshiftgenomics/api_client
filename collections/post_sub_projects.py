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
  collection = api_mosaic.get_project(args.project_id)

  # Check that this is a collection
  if not collection.data['is_collection']:
    fail('Supplied project id (' + args.project_id + ') needs to be the id of a collection')

  # Add the projects to the collection
  projects_to_add = args.projects_to_add.split(',') if ',' in args.projects_to_add else [args.projects_to_add]
  try:
    collection.post_sub_projects(collection_projects = projects_to_add, same_role = 'true')
  except Exception as e:
    fail('Failed to post sub-project with error: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project

  # The project id of the collection to add projects to
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id of the collection to add projects to')

  # The project ids to add to the collection
  project_arguments.add_argument('--projects_to_add', '-r', required = True, metavar = 'string', help = 'A comma separated list of projects to add to the collection')

  return parser.parse_args()

if __name__ == "__main__":
  main()
