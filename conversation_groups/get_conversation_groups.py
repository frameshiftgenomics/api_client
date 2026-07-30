import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Get all of the attribute forms
  data = api_mosaic.get_conversation_groups()
  if data:
    for group in data:
      print(group['name'], ', id: ', group['id'], sep = '')
      print('  Description: ', group['description'], sep = '')
      print('  Members')
      for user_id in group['user_ids']:
        user_info = api_mosaic.get_user_info(user_id)
        print('    ', user_info['first_name'], ' ', user_info['last_name'], ' (', user_info['username'], ', ', user_info['id'], ')', sep = '')

# Input options
def parse_command_line():
  parser, groups = base_parser()

  return parser.parse_args()

if __name__ == "__main__":
  main()
