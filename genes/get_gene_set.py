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

  # Get the gene sets
  gene_set = project.get_gene_set(args.gene_set_id)
  pprint(gene_set)

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to GET the gene set from')

  # The gene set id to delete
  required_arguments.add_argument('--gene_set_id', '-i', required = True, metavar = 'integer', help = 'The id of the gene set to delete')

  return parser.parse_args()

if __name__ == "__main__":
  main()
