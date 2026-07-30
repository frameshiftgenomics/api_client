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

  # Add the user to the project
  #collection.post_collection_role(user_id, role_type_id, can_download=None, can_launch_app=None, cascade_add=None)

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The project id of the collection to add projects to
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id of the collection to add projects to')

  # The name of the sample to add
  parser.add_argument('--projects_to_add', '-r', required = True, metavar = 'string', help = 'A comma separated list of projects to add to the collection')

  return parser.parse_args()

if __name__ == "__main__":
  main()
