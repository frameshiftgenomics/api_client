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

  # Open an api client project object for the defined project
  try:
    project = api_mosaic.get_project(args.project_id)
  except Exception as e:
    fail('Failed to open a project with the given id')

  # Check the HPO terms are valid
  hpo_ids = args.hpo_ids.split(',')

  # Post the HPO terms to the sample
  for hpo_id in hpo_ids:
    try:
      project.post_sample_hpo_term(args.sample_id, hpo_id)
    except Exception as e:
      print('Failed to POST the following HPO term (this will occur if the term is already present for the sample): ', str(hpo_id), sep = '')

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

  # Get the id of the project and the sample whose HPO terms are required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The project id')
  project_arguments.add_argument('--sample_id', '-s', required = True, metavar = 'integer', help = 'The id of the sample whose HPO terms are required')

  # A list of HPO terms to add
  required_arguments.add_argument('--hpo_ids', '-i', required = True, metavar = 'string', help = 'A comma separated list of terms in the format HP:00001,HP:00002')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
