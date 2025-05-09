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
  api_store  = Store(config_file = args.client_config)
  api_mosaic = Mosaic(config_file = args.client_config)

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # Get the optional information
  description = args.description if args.description else None
  is_public_to_project = 'true' if args.is_public_to_project else 'false'

  # If gene names are provided, check that they exist
  gene_names = []
  if args.gene_names:
    gene_names = args.gene_names.split(',') if ',' in args.gene_names else [args.gene_names]

  # Create the gene set
  data = project.post_gene_sets(args.name, description = description, is_public_to_project = is_public_to_project, gene_names = gene_names)

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # The name of the gene set
  parser.add_argument('--name', '-n', required = True, metavar = 'string', help = 'The name of the gene set')

  # Optional arguments
  parser.add_argument('--description', '-d', required = False, metavar = 'string', help = 'The description of the gene set')
  parser.add_argument('--is_public_to_project', '-u', required = False, action = 'store_true', help = 'Publish this gene set for everyone in the project')
  #parser.add_argument('--gene_ids', '-i', required = False, metavar = 'string', help = 'A comma separated list of gene ids')
  parser.add_argument('--gene_names', '-m', required = False, metavar = 'string', help = 'A comma separated list of gene names')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
