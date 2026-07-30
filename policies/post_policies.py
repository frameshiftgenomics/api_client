import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Create the new policy
  api_mosaic.post_policies(args.name, args.description)

# Input options
def parse_command_line():
  parser, groups = base_parser()
  required_arguments = groups.required

  # The policy name
  required_arguments.add_argument('--name', '-n', required = True, metavar = 'string', help = 'The policy name')

  # The policy description
  required_arguments.add_argument('--description', '-d', required = True, metavar = 'string', help = 'The policy description')

  return parser.parse_args()

if __name__ == "__main__":
  main()
