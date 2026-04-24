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

  # Open an api client project object for the source project
  try:
    source_project = api_mosaic.get_project(args.source_project_id)
  except Exception as e:
    fail('Failed to open project. Error was: ' + str(e))

  # Either the set id or name must be supplied
  if not args.id and not args.name:
    fail('please supply either the id or name of the gene set to copy')

  # Get the gene set
  gene_sets = {}
  for gene_set in source_project.get_gene_sets():
    set_id = gene_set['id']
    set_name = gene_set['name']

    # If the id is given, check if these match
    if args.id and int(args.id) == int(set_id):
      gene_sets[set_id] = {'name': set_name, 'description': gene_set['description'], 'gene_ids': gene_set['gene_ids']}
      break

    # Otherwise, if the name is given, use this to check if this is a match. Since names
    # are not unique, do not terminate on a name match, but check that there are no other
    # matching sets
    elif args.name and args.name == set_name:
      gene_sets[set_id] = {'name': set_name, 'description': gene_set['description'], 'gene_ids': gene_set['gene_ids']}

  # Throw an error if the gene set did not exist
  if len(gene_sets) == 0:
    fail('could not find gene set with the given name')

  # If a single set was found, copy this set
  elif len(gene_sets) == 1:
    set_id = list(gene_sets.keys())[0]
    name = gene_sets[set_id]['name']
    description = gene_sets[set_id]['description']
    gene_ids = gene_sets[set_id]['gene_ids']

    project_ids = args.destination_project_ids.split(',')
    for project_id in project_ids:

      # Open an api client project object for the defined project
      try:
        destination_project = api_mosaic.get_project(project_id)
      except Exception as e:
        fail('Failed to open destinateion project with id: ' + str(project_id) + '. Error was: ' + str(e))

      # Create the gene set
      try:
        destination_project.post_gene_sets(name, description = description, is_public_to_project = 'true', gene_ids = gene_ids)
      except Exception as e:
        fail('failed to create gene set in destination project. Error was: ' + str(e))

  # If multiple sets were found, require the id
  else:
    fail('multiple sets with the given name were found. Please use the set id, or remove duplicate set names')

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

  # Provide the ids of the project to copy from and a list of projects to copy to
  project_arguments.add_argument('--source_project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to copy the gene set from')
  project_arguments.add_argument('--destination_project_ids', '-d', required = True, metavar = 'string', help = 'A comma separated list of project ids to copy the gene set to')

  # The name of the gene set to copy
  optional_arguments.add_argument('--name', '-n', required = False, metavar = 'string', help = 'The name of the gene set to copy. If id is also set, both will be used')
  optional_arguments.add_argument('--id', '-id', required = False, metavar = 'integer', help = 'The id of the gene set to copy. If id is also set, both will be used')

  # Optional arguments
  #optional_arguments.add_argument('--description', '-d', required = False, metavar = 'string', help = 'The description of the gene set')
  #optional_arguments.add_argument('--is_public_to_project', '-u', required = False, action = 'store_true', help = 'Publish this gene set for everyone in the project')
  #parser.add_argument('--gene_ids', '-i', required = False, metavar = 'string', help = 'A comma separated list of gene ids')
  #optional_arguments.add_argument('--gene_names', '-m', required = False, metavar = 'string', help = 'A comma separated list of gene names')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
