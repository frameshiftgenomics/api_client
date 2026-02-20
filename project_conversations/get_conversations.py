import argparse
import datetime
import os

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

  # Open an api client project object for the defined project
  try:
    project = api_mosaic.get_project(args.project_id)
  except Exception as e:
    fail('Failed to open project. Error was: ' + str(e))

  # Delete watchers from the specified conversation
  for conversation in project.get_project_conversations()['data']:

    # Check the number of comments and only display this conversation if this is greater than the number specified
    # (if --minimum_comments argument was set)
    is_display = True
    if args.minimum_comments:
      is_display = True if int(conversation['comment_count']) >= int(args.minimum_comments) else False

    if is_display:
      if args.display_all_information:
        print(conversation['title'], ', id: ', conversation['id'], sep = '')
        print('  project id: ', conversation['project_id'], sep = '')
        print('  description: ', conversation['description'], sep = '')
  
        # Format the time stringd
        format_string = "%Y-%m-%dT%H:%M:%S.%fZ"
        created_at = str(datetime.strptime(conversation['created_at'], format_string)).split('.')[0]
        updated_at = str(datetime.strptime(conversation['updated_at'], format_string)).split('.')[0]
        print('  created at: ', created_at, ', updated at: ', updated_at, sep = '')
        print('  comment count: ', conversation['comment_count'], sep = '')
      else:
        print(conversation['id'], ': ', conversation['title'], sep = '')

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

  # The project id
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The id of the project')

  # Only output conversations with a minimum number of comments
  optional_arguments.add_argument('--minimum_comments', '-mc', required = False, metavar = 'integer', help = 'Only display conversations with at least this many comments')

  # What should be output
  display_arguments.add_argument('--display_all_information', '-da', required = False, action = 'store_true', help = 'If set, all information will be displayed')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
