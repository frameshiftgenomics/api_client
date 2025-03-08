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

  # Set up the experiment information
  description = args.description if args.description else None
  experiment_type = args.experiment_type if args.experiment_type else None
  if args.file_ids:
    file_ids = args.file_ids.split(',') if ',' in args.file_ids else [args.file_ids]
  else:
    file_ids = None

  # Create the new experiment
  project.post_experiment(name = args.name, description = description, experiment_type = experiment_type, file_ids = file_ids)

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

  # The project id
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id')

  # The things to add to the experiment
  parser.add_argument('--name', '-n', required = True, metavar = 'string', help = 'The name of the experiment to create')
  parser.add_argument('--description', '-d', required = False, metavar = 'string', help = 'An optional description of the experiment')
  parser.add_argument('--experiment_type', '-t', required = False, metavar = 'string', help = 'An optional type, e.g. WGS, RNA')
  parser.add_argument('--file_ids', '-f', required = False, metavar = 'integer', help = 'An optional (but recommended) comma separated list of file ids to add to the experiment')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
