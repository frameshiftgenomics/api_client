import os
import argparse

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
  project = api_mosaic.get_project(args.project_id)

  # Post the file
  endpoint_url = args.endpoint_url if args.endpoint_url else None
  project.post_project_file(name = args.name, file_type = args.file_type, uri = args.uri, reference = args.reference, endpoint_url = endpoint_url)

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # Arguments related to the file to add
  parser.add_argument('--name', '-n', required = True, metavar = 'string', help = 'The name of the file being attached')
  parser.add_argument('--file_type', '-t', required = True, metavar = 'string', help = 'The file type of the file being attached')
  parser.add_argument('--uri', '-u', required = True, metavar = 'string', help = 'The uri of the file being attached')
  parser.add_argument('--reference', '-r', required = True, metavar = 'string', help = 'The project reference')

  # Optional arguments
  parser.add_argument('--endpoint_url', '-d', required = False, metavar = 'string', help = 'The endpoint url of the file being attached')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
