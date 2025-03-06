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
  from mosaic import Mosaic, Project, Store
  api_store = Store(config_file = args.client_config)
  api_mosaic = Mosaic(config_file = args.client_config)

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # Get all project files
  for project_file in project.get_project_files():
    if args.verbose:
      print(project_file['name'])
      print('  id: ', project_file['id'], sep = '')
      print('  nickname: ', project_file['nickname'], sep = '')
      print('  type: ', project_file['type'], sep = '')
      print('  endpoint_url: ', project_file['endpoint_url'], sep = '')
      print('  experiment_ids: ', project_file['experiment_ids'], sep = '')
      print('  library_type: ', project_file['library_type'], sep = '')
      print('  reference: ', project_file['reference'], sep = '')
      print('  s3_bucket_id: ', project_file['s3_bucket_id'], sep = '')
      print('  s3_bucket_name: ', project_file['s3_bucket_name'], sep = '')
      print('  uri: ', project_file['uri'], sep = '')
    else:
      print(project_file['name'], ': ', project_file['id'], sep = '')

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

  # The project id
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id')

  # Verbose output
  parser.add_argument('--verbose', '-v', required = False, action = 'store_true', help = 'If set, provide a verbose output')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
