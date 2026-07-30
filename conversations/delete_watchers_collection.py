import os
import json
import sys

from os.path import exists
from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, warning, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)
  collection = api_mosaic.get_project(args.project_id)

  # Check if this is a collection
  data = collection.get_project()
  if not data['is_collection']:
    fail('Supplied project id (' + args.project_id + ') is for a project, not a collection')

  # Get the user ids in an array
  user_ids = args.user_ids.split(',') if ',' in args.user_ids else [args.user_ids]

  # Loop over the collection projects
  for project_info in data['collection_projects']:
    project_id = project_info['child_project_id']
    project = api_mosaic.get_project(project_id)
    print('Removing watchers from project ', str(project_id), ' - ', project.name, sep = '')

    # Get the conversations in the project
    conversations = project.get_project_conversations()
    if 'data' in conversations:
      for conversation in conversations['data']:
        try:
          project.delete_watchers(conversation['id'], user_ids)
        except:
          pass

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # A comma separated list of users to remove as watchers from the conversation
  parser.add_argument('--user_ids', '-u', required = True, metavar = 'string', help = 'A comma separated list of users to remove as watchers from the conversation')

  return parser.parse_args()

# Throw a warning
def warning(message):
  print('WARNING: ', message, sep = '')

# Initialise global variables

if __name__ == "__main__":
  main()
