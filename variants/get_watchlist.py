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

  # Get the variant sets in the project
  include_variant_data = 'true' if args.include_variant_data else 'false'
  try:
    data = project.get_variant_watchlist(include_variant_data = include_variant_data)
  except Exception as e:
    fail('Failed to get variant watchlist. Error was: ' + str(e))

  # If only the number of variants is required
  if args.output_number_variants:
    print(len(data['variant_ids']))

  # Format the output based on whether variants were output
  else:
    print(data['name'], ': ', data['id'], sep = '')
    print('  description: ', data['description'], sep = '')
    print('  is_watchlist: ', data['is_watchlist'], sep = '')
    print('  is_public_to_project: ', data['is_public_to_project'], sep = '')
    print('  Number of variants: ', len(data['variant_ids']), sep = '')

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  optional_arguments = groups.optional
  display_arguments = groups.display

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to add variant filters to')

  # Should variant data be returned
  optional_arguments.add_argument('--include_variant_data', '-i', required = False, action = 'store_true', help = 'Should variant data be returned')

  # Display options
  display_arguments.add_argument('--output_number_variants', '-nv', required = False, action = 'store_true', help = 'Only output the number of variants in the watchlist')

  return parser.parse_args()

if __name__ == "__main__":
  main()
