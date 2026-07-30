import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Loop over the role types and get information
  role_types = {}
  for role_information in api_mosaic.get_role_types():
    role_types[role_information['id']] = {'name': role_information['display_name'], \
                                          'id': role_information['id'], \
                                          'level': role_information['level'], \
                                          'access_level': role_information['access_level']}

# Print out the roles
  for role_id in sorted(role_types.keys()):
    print(role_types[role_id]['name'], sep = '')
    print('  id: ', role_types[role_id]['id'], sep = '')
    print('  level: ', role_types[role_id]['level'], sep = '')
    print('  access_level: ', role_types[role_id]['access_level'], sep = '')

# Input options
def parse_command_line():
  parser, _ = base_parser()

  return parser.parse_args()

if __name__ == "__main__":
  main()
