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
  try:
    from mosaic import Mosaic, Project, Store
  except:
    fail('Cannot find mosaic. Please set the --api_client / -a argument')
  api_store = Store(config_file = args.client_config)
  api_mosaic = Mosaic(config_file = args.client_config)

  # If the api_client path was not specified, get it from the script path
  if not args.api_client:
    try:
      args.api_client = os.path.dirname(os.path.realpath(__file__)).split('api_client')[0] + str('api_client')
    except:
      fail('Could not get the api_client path from the command. Please specify using --api_client / -a')

  # Get the diff summary
  try:
    summary_by_project = {}
    for summary in api_mosaic.get_clinvar_diff_summary(args.annotation_version_id_a, args.annotation_version_id_b):
      project_id = summary['project_id']
      if project_id not in summary_by_project:
        summary_by_project[project_id] = [summary]
      else:
        summary_by_project[project_id].append(summary)

    # Print out the data
    for project_id in summary_by_project:
      print('Project:', project_id)
      for summary in summary_by_project[project_id]:
        print(summary)
  except Exception as e:
    fail('failed to get summary. Error was: ' + str(e))

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

  # The ClinVar versions to diff
  required_arguments.add_argument('--annotation_version_id_a', '-va', required = True, metavar = 'integer', help = 'The old ClinVar annotation version id')
  required_arguments.add_argument('--annotation_version_id_b', '-vb', required = True, metavar = 'integer', help = 'The new ClinVar annotation version id')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  message = 'ERROR: ' + message
  print(message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
