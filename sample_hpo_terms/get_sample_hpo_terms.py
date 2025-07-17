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
  project = api_mosaic.get_project(args.project_id)

  # If the terms should be output for Exomiser, collect them in a list first
  if args.exomiser_format:
    hpo_terms = []
    for hpo_term in project.get_sample_hpo_terms(args.sample_id):
      hpo_terms.append(hpo_term['hpo_id'])
    print(hpo_terms)

  # Get the HPO terms for the sample
  else:
    for hpo_term in project.get_sample_hpo_terms(args.sample_id):
      print(hpo_term['hpo_id'], ': ', hpo_term['label'], ' (id: ', hpo_term['id'], ')', sep = '')

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

  # Output in a format for exomiser
  project_arguments.add_argument('--exomiser_format', '-e', required = False, action = 'store_true', help = 'Output the HPO terms in a format useful for Exomiser')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
