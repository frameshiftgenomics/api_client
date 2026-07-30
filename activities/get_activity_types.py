import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():
  global api_mosaic
  global allowed_references
  global system_projects

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  try:
    activity_types = {}
    for activity_type in api_mosaic.get_activity_types()['data']:
      activity_types[activity_type['id']] = activity_type['type']
    for activity_type_id in sorted(activity_types.keys()):
      print('id: ', activity_type_id, ', type: ', activity_types[activity_type_id], sep = '')
  except Exception as e:
    fail('failed to get activity types. Error was: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()

  return parser.parse_args()

api_mosaic = None

if __name__ == "__main__":
  main()
