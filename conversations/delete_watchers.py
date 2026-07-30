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

  # Get the user ids in an array
  user_ids = args.user_ids.split(',') if ',' in args.user_ids else [args.user_ids]

  # Delete watchers from the specified conversation
  project.delete_watchers(args.conversation_id, user_ids)

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The project id
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The id of the project to delete')

  # The id of the conversation to remove watchers from
  parser.add_argument('--conversation_id', '-n', required = True, metavar = 'integer', help = 'The id of the conversation to remove watchers from')

  # A comma separated list of users to remove as watchers from the conversation
  parser.add_argument('--users', '-u', required = True, metavar = 'string', help = 'A comma separated list of users to remove as watchers from the conversation')

  return parser.parse_args()

if __name__ == "__main__":
  main()
