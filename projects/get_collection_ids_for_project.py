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
  
  try:
    for collection in  project.get_project()['member_of_collections']:
      if args.ids_only:
        print(collection['id'])
      else:
        print(collection['id'], ': ', collection['name'], sep = '')
  except Exception as e:
    fail('Failed to get information on project collections. Error was: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  display_arguments = groups.display

  # The id of the project
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'string', help = 'The id of the project')

  # Only write out the collection ids
  display_arguments.add_argument('--ids_only', '-io', required = False, action = 'store_true', help = 'Only return project ids for the collections')

  return parser.parse_args()

if __name__ == "__main__":
  main()
