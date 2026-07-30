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
    collection = api_mosaic.get_project(args.project_id)
  except Exception as e:
    fail('failed to open collection. Error was: ' + str(e))

  # Check that this is a collection
  if not collection.data['is_collection']:
    fail('Supplied project id (' + args.project_id + ') needs to be the id of a collection')

  # Add the projects to the collection
  projects_to_delete = []
  for udn_id in args.projects_to_delete.split(','):
    projects_to_delete.append(str(udn_id))
  try:
    data = collection.delete_sub_projects(projects_to_delete)
  except Exception as e:
    fail('failed to delete projects. Error was: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required

  # The project id of the collection to add projects to
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id of the collection to add projects to')

  # The name of the sample to add
  required_arguments.add_argument('--projects_to_delete', '-d', required = True, metavar = 'string', help = 'A comma separated list of projects to delete from the collection')

  return parser.parse_args()

if __name__ == "__main__":
  main()
