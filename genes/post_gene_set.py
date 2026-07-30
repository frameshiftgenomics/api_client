import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Open an api client project object for the defined project
  try:
    project = api_mosaic.get_project(args.project_id)
  except Exception as e:
    fail('Failed to open project. Error was: ' + str(e))

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
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required
  optional_arguments = groups.optional

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to POST gene set to')

  # The name of the gene set
  required_arguments.add_argument('--name', '-n', required = True, metavar = 'string', help = 'The name of the gene set')

  # Optional arguments
  optional_arguments.add_argument('--description', '-d', required = False, metavar = 'string', help = 'The description of the gene set')
  optional_arguments.add_argument('--is_public_to_project', '-u', required = False, action = 'store_true', help = 'Publish this gene set for everyone in the project')
  #parser.add_argument('--gene_ids', '-i', required = False, metavar = 'string', help = 'A comma separated list of gene ids')
  optional_arguments.add_argument('--gene_names', '-m', required = False, metavar = 'string', help = 'A comma separated list of gene names')

  return parser.parse_args()

if __name__ == "__main__":
  main()
