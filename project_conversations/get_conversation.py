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

  # Delete watchers from the specified conversation
  
  try:
    for conversation in project.get_project_conversation(args.conversation_id):
      print(conversation['title'], ', id: ', conversation['id'], sep = '')

      # Format the time stringd
      format_string = "%Y-%m-%dT%H:%M:%S.%fZ"
      created_at = str(datetime.strptime(conversation['created_at'], format_string)).split('.')[0]
      updated_at = str(datetime.strptime(conversation['updated_at'], format_string)).split('.')[0]
      print('  conversation watcher: ', conversation['user_is_watcher'], sep = '')
      print('  created at: ', created_at, sep = '')
      print('  updated at: ', updated_at, sep = '')
      print('  conversation comments:')
      for comment in conversation['comments']:
        user_id = comment['user_id']
        user_info = api_mosaic.get_user_info(user_id)
        username = user_info['username']
        first_name = user_info['first_name']
        last_name = user_info['last_name']
        format_string = "%Y-%m-%dT%H:%M:%S.%f%z"
        clean_value = comment['created_at'][:-3] + comment['created_at'][-2:]
        created_at = str(datetime.strptime(clean_value, format_string)).split('.')[0]
        print('    id: ', comment['id'], ', user_id: ', user_id, ', username: ', username, ' (', first_name, ' ', last_name, '), created at: ', created_at, sep = '')
        if args.include_text:
          print('      ', comment['text'], sep = '')
  except Exception as e:
    fail('failed to get information for this conversation. Error was: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required
  optional_arguments = groups.optional

  # The project id
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The id of the project')

  # The conversation id
  required_arguments.add_argument('--conversation_id', '-i', required = True, metavar = 'integer', help = 'The id of the conversation')

  # Include comment text
  optional_arguments.add_argument('--include_text', '-t', required = False, action = 'store_true', help = 'Include commend text in the output')

  return parser.parse_args()

if __name__ == "__main__":
  main()
