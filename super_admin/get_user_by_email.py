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
  try:
    print(api_mosaic.get_user_by_email(args.email)['user_id'])
  except:
    print(args.email, ' does not exist')

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The users email address
  parser.add_argument('--email', '-e', required = True, metavar = 'string', help = 'The email of the user to get')

  return parser.parse_args()

if __name__ == "__main__":
  main()
