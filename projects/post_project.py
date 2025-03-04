import os
import argparse

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
  from mosaic import Mosaic, Project, Store
  api_store = Store(config_file = args.client_config)
  api_mosaic = Mosaic(config_file = args.client_config)

  # Check that the reference is valid
  allowed_references = ['GRCh37', 'GRCh38']
  if args.reference not in allowed_references:
    fail('unknown reference')

  # Check the privacy level is allowed
  allowed_privacy = ['public', 'protected', 'private']
  args.privacy_level = 'private' if not args.privacy_level else args.privacy_level
  if args.privacy_level not in allowed_privacy:
    fail('unknown privacy level')
  
  # Create a project
  project = api_mosaic.post_project(args.name, args.reference, nickname = args.nickname, description = args.description, is_collection = args.is_collection, privacy_level = args.privacy_level)

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

  # The project information
  parser.add_argument('--name', '-n', required = True, metavar = 'string', help = 'The project name')
  parser.add_argument('--reference', '-r', required = True, metavar = 'string', help = 'The project reference')
  parser.add_argument('--nickname', '-m', required = False, metavar = 'string', help = 'The project nickname')
  parser.add_argument('--description', '-d', required = False, metavar = 'string', help = 'The project description')
  parser.add_argument('--privacy_level', '-l', required = False, metavar = 'string', help = 'The projects privacy level. Default: private')
  parser.add_argument('--is_collection', '-co', required = False, action = 'store_true', help = 'Set if this is to be a collection, not a project')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
