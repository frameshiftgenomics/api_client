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

  # Check for mutually exclusive arguments
  if args.no_comments and args.minimum_comments:
    fail('cannot simultaneously request conversations with no comments and a minimum number of comments')

  # Open an api client project object for the defined project
  try:
    project = api_mosaic.get_project(args.project_id)
  except Exception as e:
    fail('Failed to open project. Error was: ' + str(e))

  # Delete watchers from the specified conversation
  for conversation in project.get_project_conversations()['data']:

    # Check the number of comments and only display this conversation if this is greater than the number specified
    # (if --minimum_comments argument was set)
    is_display = True
    if args.minimum_comments:
      is_display = True if int(conversation['comment_count']) >= int(args.minimum_comments) else False
    elif args.no_comments:
      if int(conversation['comment_count']) > 0:
        is_display = False

    if args.name:
      if str(args.name) != str(conversation['title']):
        is_display = False

    if is_display:
      if args.display_all_information:
        print(conversation['title'], ', id: ', conversation['id'], sep = '')
        print('  project id: ', conversation['project_id'], sep = '')
        print('  description: ', conversation['description'], sep = '')
  
        # Format the time stringd
        format_string = "%Y-%m-%dT%H:%M:%S.%fZ"
        created_at = str(datetime.strptime(conversation['created_at'], format_string)).split('.')[0]
        updated_at = str(datetime.strptime(conversation['updated_at'], format_string)).split('.')[0]
        print('  created at: ', created_at, ', updated at: ', updated_at, sep = '')
        print('  comment count: ', conversation['comment_count'], sep = '')
      elif args.output_ids_only:
        print(conversation['id'])
      else:
        print(conversation['id'], ': ', conversation['title'], sep = '')

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  optional_arguments = groups.optional
  display_arguments = groups.display

  # The project id
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The id of the project')

  # Only output conversations with the given name
  optional_arguments.add_argument('--name', '-n', required = False, metavar = 'string', help = 'only display conversations with this name')

  # Only output conversations with a minimum number of comments or no comments
  optional_arguments.add_argument('--no_comments', '-nc', required = False, action = 'store_true', help = 'only display conversations with no comments')
  optional_arguments.add_argument('--minimum_comments', '-mc', required = False, metavar = 'integer', help = 'only display conversations with at least this many comments')

  # What should be output
  display_arguments.add_argument('--display_all_information', '-da', required = False, action = 'store_true', help = 'If set, all information will be displayed')
  display_arguments.add_argument('--output_ids_only', '-io', required = False, action = 'store_true', help = 'If set, only conversation ids will be output')

  return parser.parse_args()

if __name__ == "__main__":
  main()
