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
  data = api_mosaic.get_global_settings()
  pprint(data)

# Input options
def parse_command_line():
  parser, groups = base_parser()

  return parser.parse_args()

if __name__ == "__main__":
  main()
