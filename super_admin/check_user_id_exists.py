import datetime
import os
import sys
import time

from datetime import datetime
from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Get the user info
  try:
    user_data = api_mosaic.get_user_info(args.user_id)
  except Exception as e:
    fail('Unable to get user info. Error was: ' + str(e))

  # Format the time stringd
  format_string = "%Y-%m-%dT%H:%M:%S.%fZ"
  try:
    created_at = str(datetime.strptime(user_data['created_at'], format_string)).split('.')[0]
  except:
    created_at = None
  try:
    last_login_at = str(datetime.strptime(user_data['last_login_at'], format_string)).split('.')[0]
  except:
    last_login_at = None

  # Write out the information
  if args.last_login:
    print(user_data['first_name'], ' ', user_data['last_name'], ': ', last_login_at, sep = '')

  # Write all data
  else:
    print(user_data['id'], ': ', sep = '')
    print('  email: ', user_data['email'], sep = '')
    print('  first name: ', user_data['first_name'], sep = '')
    print('  last name: ', user_data['last_name'], sep = '')
    print('  username: ', user_data['username'], sep = '')
    print('  CAS username: ', user_data['cas_username'], sep = '')
    print('  created: ', created_at, sep = '')
    print('  confirmation status: ', user_data['confirmation_status'], sep = '')
    print('  last login: ', last_login_at, sep = '')

# Input options
def parse_command_line():
  parser, groups = base_parser()
  required_arguments = groups.required

  # The user id
  required_arguments.add_argument('--user_id', '-i', required = True, metavar = 'integer', help = 'The user id')

  return parser.parse_args()

if __name__ == "__main__":
  main()
