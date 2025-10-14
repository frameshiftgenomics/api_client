import argparse
import datetime
import os
import time

from datetime import datetime
from pprint import pprint
from sys import path

def main():

  # Parse the command line
  args = parse_command_line()

  # If the api_client path was not specified, get it from the script path
  if not args.api_client:
    try:
      args.api_client = os.path.dirname(os.path.realpath(__file__)).split('api_client')[0] + str('api_client')
    except:
      fail('Could not get the api_client path from the command. Please specify using --api_client / -a')

  # Import the api client
  path.append(args.api_client)
  try:
    from mosaic import Mosaic, Project, Store
  except:
    fail('Cannot find mosaic. Please set the --api_client / -a argument')
  api_store = Store(config_file = args.client_config)
  api_mosaic = Mosaic(config_file = args.client_config)

  # Get the user info
  user_data = api_mosaic.get_user_info(args.user_id)

  # Format the time stringd
  format_string = "%Y-%m-%dT%H:%M:%S.%fZ"
  created_at = str(datetime.strptime(user_data['created_at'], format_string)).split('.')[0]
  last_login_at = str(datetime.strptime(user_data['last_login_at'], format_string)).split('.')[0]

  # Write out the information
  if args.last_login:
    print(last_login_at)

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
  parser = argparse.ArgumentParser(description='Process the command line arguments')
  api_arguments = parser.add_argument_group('API Arguments')
  project_arguments = parser.add_argument_group('Project Arguments')
  required_arguments = parser.add_argument_group('Required Arguments')
  optional_arguments = parser.add_argument_group('Optional Arguments')
  display_arguments = parser.add_argument_group('Display Information')

  # Define the location of the api_client and the ini config file
  api_arguments.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  api_arguments.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

  # The user id
  required_arguments.add_argument('--user_id', '-i', required = True, metavar = 'integer', help = 'The user id')

  # Optional display arguments
  display_arguments.add_argument('--last_login', '-l', required = False, action = 'store_true', help = 'If set, only the last login date will be output for the user')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
