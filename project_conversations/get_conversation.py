import os
import argparse

from pprint import pprint
from sys import path

def main():

  # Parse the command line
  args = parse_command_line()

  # Import the api client
  path.append(args.api_client)
  from mosaic import Mosaic, Project, Store
  api_store  = Store(config_file = args.client_config)
  api_mosaic = Mosaic(config_file = args.client_config)

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # Delete watchers from the specified conversation
  data = project.get_project_conversation(args.conversation_id)
  for conversation in data:
    print('Conversation: ', conversation['title'], sep = '')
    for comment in conversation['comments']:
      user_id = comment['user_id']
      user_info = api_mosaic.get_user_info(user_id)
      username = user_info['username']
      first_name = user_info['first_name']
      last_name = user_info['last_name']
      print('  id: ', comment['id'], ', user_id: ', user_id, ', username: ', username, ' (', first_name, ' ', last_name, ')', sep = '')

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = True, metavar = 'string', help = 'The api_client directory')

  # The project id
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The id of the project')

  # The conversation id
  parser.add_argument('--conversation_id', '-i', required = True, metavar = 'integer', help = 'The id of the conversation')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print(message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
