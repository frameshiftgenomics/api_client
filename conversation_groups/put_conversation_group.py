import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Get the existing conversation group
  for group in api_mosaic.get_conversation_groups():
    if int(group['id']) == int(args.group_id):
      existing_name = group['name']
      existing_description = group['description']
      existing_user_ids = group['user_ids']
      break

  # Create a new conversation group
  name = args.name if args.name else existing_name
  description = args.description if args.description else existing_description
  if args.user_ids:
    user_ids = args.user_ids.split(',') if ',' in args.user_ids else [args.user_ids]
  else:
    user_ids = existing_user_ids

  # Update the conversation group
  try:
    data = api_mosaic.put_conversation_groups(args.group_id, name = name, description = description, user_ids = user_ids)
  except Exception as e:
    fail('Failed to update the conversation group. Error: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  required_arguments = groups.required
  optional_arguments = groups.optional

  # The id of the conversation group
  required_arguments.add_argument('--group_id', '-i', required = True, metavar = 'integer', help = 'The id of the conversation group')

  # Get information on the conversation group
  optional_arguments.add_argument('--name', '-n', required = False, metavar = 'string', help = 'The name of the conversation group')
  optional_arguments.add_argument('--user_ids', '-u', required = False, metavar = 'string', help = 'A comma separated list of user ids to add to the conversation group')
  optional_arguments.add_argument('--description', '-d', required = False, metavar = 'string', help = 'A description of the conversation group')

  return parser.parse_args()

if __name__ == "__main__":
  main()
