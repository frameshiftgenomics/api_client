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

  # If categories were supplied, break up the list
  categories = []
  if args.categories:
    categories = args.categories.split(',') if ',' in args.categories else [args.categories]

  # Get the list of variant filter ids
  for variant_filter in project.get_variant_filters():
    display = True
    if args.categories and variant_filter['category'] not in categories:
      display = False

    # Only display if the filter is in a specified category, or no categories were specified
    if display:
      if args.display_all:
        print(variant_filter['name'])
        for field in variant_filter:
          if field != 'name':
            print('  ', field, ': ', variant_filter[field], sep = '')
      else:
        print(variant_filter['id'])

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  display_arguments = groups.display

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to add variant filters to')

  # Display options
  display_arguments.add_argument('--display_all', '-da', required = False, action = 'store_true', help = 'Output all variant filter information')
  display_arguments.add_argument('--categories', '-ca', required = False, metavar = 'string', help = 'Comma separated list of categories. Only filters in these categories will be returned')

  return parser.parse_args()

if __name__ == "__main__":
  main()
