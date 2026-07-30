import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Some display options are mutually exclusive
  if args.display_all_information and args.ids_only:
    fail('The --display_all_information (-da) and --ids_only (-io) arguments are mututally exclusive')

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # Get the extensions to find
  types = []
  if args.file_types:
    types = args.file_types.split(',') if ',' in args.file_types else [args.file_types]

  # Get all of the sample files
  for sample in project.get_sample_files(args.sample_id):
    display = True
    if args.file_types and sample['type'] not in types:
      display = False

    if display:
      if args.ids_only:
        print(sample['id'])
      elif not args.display_all_information:
        print(sample['name'], ': ', sample['id'], ', ', sample['type'], sep = '')
      else:
        print(sample['name'])
        print('  id: ', sample['id'], sep = '')
        print('  type: ', sample['type'], sep = '')
        print('  uri: ', sample['uri'], sep = '')
        print('  vcf sample name: ', sample['vcf_sample_name'], sep = '')

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required
  optional_arguments = groups.optional
  display_arguments = groups.display

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # Arguments related to the file to add
  required_arguments.add_argument('--sample_id', '-s', required = True, metavar = 'string', help = 'The sample id the file is attached to')

  # Which file extensions to return
  optional_arguments.add_argument('--file_types', '-t', required = False, metavar = 'string', help = 'A comma separated list of extensions to return')

  # Determine what information to print to screen
  display_arguments.add_argument('--display_all_information', '-da', required = False, action = 'store_true', help = 'Display all information about the attributes')
  display_arguments.add_argument('--ids_only', '-io', required = False, action = 'store_true', help = 'Output the file ids only')

  return parser.parse_args()

if __name__ == "__main__":
  main()
