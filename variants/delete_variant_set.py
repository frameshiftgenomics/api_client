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
  project = api_mosaic.get_project(args.project_id)

  # Get the variant sets in the project
  variant_set_ids = [args.variant_set_ids] if ',' not in args.variant_set_ids else args.variant_set_ids.split(',')
  for variant_set_id in variant_set_ids:
    data = project.delete_variant_set(variant_set_id)

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to add variant filters to')

  # A comma separated list of variant set ids to delete
  parser.add_argument('--variant_set_ids', '-v', required = True, metavar = 'string', help = 'A comma separate list of variant set ids to delete')

  return parser.parse_args()

if __name__ == "__main__":
  main()
