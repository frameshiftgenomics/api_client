import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Delete the policy
  project.delete_policies(args.policy_id)

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The policy id to delete
  parser.add_argument('--policy_id', '-i', required = True, metavar = 'integer', help = 'The policy id to delete')

  return parser.parse_args()

if __name__ == "__main__":
  main()
