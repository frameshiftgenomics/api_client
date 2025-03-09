import os
import argparse

from sys import path

def main():

  # Parse the command line
  args = parse_command_line()

  # If the api_client path was not specified, get it from the script path
  if args.api_client:
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
  apiStore  = Store(config_file = args.client_config)
  apiMosaic = Mosaic(config_file = args.client_config)

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # Upload the variant annotations
  allow_deletion = 'true' if args.allow_deletion else 'false'
  disable_successful_notification = 'true' if args.disable_successful_notification else 'false'
  data = project.post_annotation_file(args.tsv, allow_deletion = allow_deletion, disable_successful_notification = disable_successful_notification)
  print(data['message'], '. Annotation upload job id: ', data['redis_job_id'], ', file: ', args.tsv, sep = '')

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to add variant filters to')

  # Additional arguments
  parser.add_argument('--tsv', '-t', required = True, metavar = 'string', help = 'The annotation tsv file to upload')
  parser.add_argument('--allow_deletion', '-d', required = False, action = 'store_true', help = 'If tsv file contains blank annotation, overwrite the existing value in the database will null. Default: false')
  parser.add_argument('--disable_successful_notification', '-n', required = False, action = 'store_false', help = 'Only send notifications if the upload fails. Default: true')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
