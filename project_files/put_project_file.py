import os
import argparse

from sys import path

def main():

  # Parse the command line
  args = parse_command_line()

  # Import the api client
  path.append(args.api_client)
  from mosaic import Mosaic, Project, Store
  api_store = Store(config_file = args.client_config)
  api_mosaic = Mosaic(config_file = args.client_config)

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # Update the file
  project.put_project_file(file_id = args.file_id, name = args.name, nickname = args.nickname, file_type = args.file_type, uri = args.uri, reference = args.reference, endpoint_url = args.endpoint_url)

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = True, metavar = 'string', help = 'The api_client directory')

  # The project and file id
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id')
  parser.add_argument('--file_id', '-f', required = True, metavar = 'integer', help = 'The Mosaic file id')

  # Arguments related to the file to add
  parser.add_argument('--name', '-n', required = False, metavar = 'string', help = 'The name of the file being attached')
  parser.add_argument('--nickname', '-k', required = False, metavar = 'string', help = 'The nickname of the file being attached')
  parser.add_argument('--file_type', '-t', required = False, metavar = 'string', help = 'The file type of the file being attached')
  parser.add_argument('--uri', '-u', required = False, metavar = 'string', help = 'The uri of the file being attached')
  parser.add_argument('--reference', '-r', required = False, metavar = 'string', help = 'The project reference')

  # Optional arguments
  parser.add_argument('--endpoint_url', '-d', required = False, metavar = 'string', help = 'The endpoint url of the file being attached')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print(message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
