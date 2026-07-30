import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Get the user info
  for project in api_mosaic.get_user_project_roles(args.user_id):
    print(project['project_name'], ': ', project['project_id'], ', ', project['role_name'], ' (', project['role_type_id'], ')', sep = '')

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The user id
  parser.add_argument('--user_id', '-i', required = True, metavar = 'integer', help = 'The user id')

  return parser.parse_args()

if __name__ == "__main__":
  main()
