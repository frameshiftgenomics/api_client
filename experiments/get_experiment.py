import os
import argparse

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

  # Get the experiment information
  experiment = project.get_experiment(args.experiment_id)
  print('name: ', experiment['name'], sep = '')
  print('id: ', experiment['id'], sep = '')
  print('description: ', experiment['description'], sep = '')
  print('type: ', experiment['type'], sep = '')
  print('number of associated files: ', experiment['file_count'], sep = '')
  print('Files:')
  for experiment_file in experiment['files']:
    print('  ', experiment_file['id'], sep = '')
    print('    name: ', experiment_file['name'], sep = '')
    print('    nickname: ', experiment_file['nickname'], sep = '')
    print('    type: ', experiment_file['type'], sep = '')
    print('    sample_id: ', experiment_file['sample_id'], sep = '')
    print('    reference: ', experiment_file['reference'], sep = '')
    if experiment_file['vcf_sample_name']:
      print('    vcf_sample_name: ', experiment_file['vcf_sample_name'], sep = '')
    print('    uri: ', experiment_file['uri'], sep = '')

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = True, metavar = 'string', help = 'The api_client directory')

  # The project id
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id')

  # The experiment id
  parser.add_argument('--experiment_id', '-e', required = True, metavar = 'integer', help = 'The experiment id')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print(message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
