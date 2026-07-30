import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # The -io and -no options are mutually exclusive
  if args.ids_only and args.names_only:
    fail('Only one of --ids_only or --names_only can be specified at a time')

  # Delete the file
  samples = project.get_samples()
  for sample in samples:

    # If only output samples is set, provide the limited output
    if args.ids_only:
      print(sample['id'], sep = '')

    # Of if only names are requested
    elif args.names_only:
      print(sample['name'], sep = '')

    # Output the name and id
    elif args.id_name_only:
      print(sample['name'], ':', sample['id'], sep = '')

    # Output all information
    else:
      print(sample['name'])
      for info in sample:
        print('  ', info, ': ', sample[info], sep = '')

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  display_arguments = groups.display

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # Output ids only
  display_arguments.add_argument('--ids_only', '-io', required = False, action = 'store_true', help = 'Only output sample ids')
  display_arguments.add_argument('--names_only', '-no', required = False, action = 'store_true', help = 'Only output sample names')
  display_arguments.add_argument('--id_name_only', '-in', required = False, action = 'store_true', help = 'Output the sample name and id')

  return parser.parse_args()

if __name__ == "__main__":
  main()
