import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  role_information = api_mosaic.get_role_type(args.role_type_id)
  print('role_id: ', role_information['id'], sep = '')
  print('name: ', role_information['display_name'], sep = '')
  print('level: ', role_information['level'], sep = '')
  print('access_level: ', role_information['access_level'], sep = '')

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The role type to GET
  parser.add_argument('--role_type_id', '-i', required = True, metavar = 'integer', help = 'The id of the role type to get')

  return parser.parse_args()

if __name__ == "__main__":
  main()
