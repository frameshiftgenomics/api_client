import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Create a new conversation group
  description = args.description if args.description else None
  user_ids = args.user_ids.split(',') if ',' in args.user_ids else [args.user_ids]
  data = api_mosaic.post_conversation_groups(args.name,  user_ids, description = description)

# Input options
def parse_command_line():
  parser, groups = base_parser()
  required_arguments = groups.required

  # Get information on the conversation group
  required_arguments.add_argument('--name', '-n', required = True, metavar = 'string', help = 'The name of the conversation group')
  required_arguments.add_argument('--user_ids', '-u', required = True, metavar = 'string', help = 'A comma separated list of user ids to add to the conversation group')
  required_arguments.add_argument('--description', '-d', required = True, metavar = 'string', help = 'A description of the conversation group')

  return parser.parse_args()

if __name__ == "__main__":
  main()
