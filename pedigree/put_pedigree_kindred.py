import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  try:
    project = api_mosaic.get_project(args.project_id)
  except Exception as e:
    fail('failed to open project. Error was: ' + str(e))

  # Update the kindred id
  try:
    project.put_pedigree_kindred(args.pedigree_id, args.kindred_id)
  except Exception as e:
    fail('failed to post pedigree. Error was: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required

  # The project and sample ids
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id')

  # Additional pedigree information
  required_arguments.add_argument('--pedigree_id', '-pi', required = True, metavar = 'string', help = 'The pedigree id')
  required_arguments.add_argument('--kindred_id', '-k', required = True, metavar = 'string', help = 'The kindred id')

  return parser.parse_args()

if __name__ == "__main__":
  main()
