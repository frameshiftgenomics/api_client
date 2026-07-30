import datetime
import os
import sys

from datetime import datetime
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

  # Delete the conversation
  try:
    project.delete_project_conversation(args.conversation_id)
  except Exception as e:
    fail('failed to delete conversation. Error was: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required

  # The project id
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The id of the project')

  # The conversation id
  required_arguments.add_argument('--conversation_id', '-i', required = True, metavar = 'integer', help = 'The id of the conversation')

  return parser.parse_args()

if __name__ == "__main__":
  main()
