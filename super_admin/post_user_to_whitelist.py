import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Post the email to the whitelist
  try:
    api_mosaic.post_to_whitelist(args.email)
  except Exception as e:
    fail('failed to add user to whitelist. Error was: ' + str(e))

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The user id
  parser.add_argument('--email', '-e', required = True, metavar = 'string', help = 'The email to add to the whitelist')

  return parser.parse_args()

if __name__ == "__main__":
  main()
