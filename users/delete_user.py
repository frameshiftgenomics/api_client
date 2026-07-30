import os
import importlib
import sys

from os.path import exists
from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)
  success = api_mosaic.delete_user(args.user_id)

# Input options
def parse_command_line():
  parser, _ = base_parser()

  parser.add_argument('--user_id', '-u', required = True, metavar = 'integer', help = 'The id of the user to delete')

  return parser.parse_args()

# Initialise global variables

if __name__ == "__main__":
  main()
