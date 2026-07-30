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

  # Set the display requirements
  include_variant_data = True if args.show_variant_data else False
  include_genotype_data = True if args.show_genotype_information else False

  # If only_show_variant_ids is set, no other display options can be set
  if args.only_show_variant_ids and (args.show_variant_data or args.show_genotype_information):
    fail('If --only_show_variant_ids (-vi) is set, no other optional display arguments can be set')

  # Get the variant set information
  try:
    variant_set_info = project.get_variant_set_watchlist(include_variant_data = include_variant_data, include_genotype_data = include_genotype_data)
  except Exception as e:
    fail('Failed to get variant set information. Error was: ' + str(e))

  # Only output variant ids
  if args.only_show_variant_ids:
    for variant_id in variant_set_info['variant_ids']:
      print(variant_id)
  elif args.only_output_count:
    if len(variant_set_info['variant_ids']) > 0:
      print(len(variant_set_info['variant_ids']))

  # Output all information
  else:
    pprint(variant_set_info)

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  display_arguments = groups.display

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to get variants sets for')

  # Optional arguments
  display_arguments.add_argument('--show_variant_data', '-si', required = False, action = 'store_true', help = 'Show the variant annotation information')
  display_arguments.add_argument('--show_genotype_information', '-sg', required = False, action = 'store_true', help = 'Show the genotype information')
  display_arguments.add_argument('--only_show_variant_ids', '-vi', required = False, action = 'store_true', help = 'Only output the ids of the variants in the set')
  display_arguments.add_argument('--only_output_count', '-oc', required = False, action = 'store_true', help = 'If set, the variant count will be output if it is greater than 0. Otherwise there will be no output')

  return parser.parse_args()

if __name__ == "__main__":
  main()
