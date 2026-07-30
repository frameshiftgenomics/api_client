import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Get the task_type_attributes
  for task_type in api_mosaic.get_task_types():
    print(task_type['display_name'])
    print('  Task type id: ', task_type['id'], sep = '')
    print('  Type: ', task_type['type'], sep = '')
    print('  Category: ', task_type['category'], sep = '')
    print('  Display Category: ', task_type['display_category'], sep = '')
    print()

# Input options
def parse_command_line():
  parser, groups = base_parser()

  return parser.parse_args()

if __name__ == "__main__":
  main()
