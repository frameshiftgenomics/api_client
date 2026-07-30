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

  # Display options are mutually exclusive
  if args.output_list and args.output_ids:
    fail('Display arguments are mutually exclusive')

  # Get all the users in the project
  output_list = ''
  for user in project.get_project_users():

    # Build the output list if requested
    if args.output_list:
      output_list += str(user['id']) + ','

    # Output the id only
    elif args.output_ids:
      print(user['id'])

    # Output all information
    else:
      print(user['first_name'], ' ', user['last_name'], ':', sep = '')
      print('  id: ', user['id'], sep = '')
      print('  username: ', user['username'], sep = '')

  # Strip the trailing comma from the output list
  if args.output_list:
    print(output_list.rstrip(','))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  display_arguments = groups.display

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # Optional viewing options
  display_arguments.add_argument('--output_ids', '-oi', required = False, action = 'store_true', help = 'Only output user ids')
  display_arguments.add_argument('--output_list', '-ol', required = False, action = 'store_true', help = 'Output a comma separated list of all user ids')

  return parser.parse_args()

if __name__ == "__main__":
  main()
