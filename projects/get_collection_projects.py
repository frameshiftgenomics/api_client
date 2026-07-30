import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # If a reference is provided, check that it's valid
  if args.reference:
    if args.reference == 'GRCh37':
      pass
    elif args.reference == 'GRCh38':
      pass
    else:
      fail('Unknown reference genome')

  # Open an api client project object for the defined project
  try:
    collection = api_mosaic.get_project(args.collection_id)
  except Exception as e:
    fail('Unable to open project with the given id. The project id must be a valid integer')
  if not collection.get_project()['is_collection']:
    fail('Collection id is for a project, not a collection')

  # Make sure conflicting display options aren't selected
  if args.ids_only and args.display_all:
    fail('Conflicting display options selected')

  # Get all projects in the collection
  output_list = ''
  for project_info in collection.get_collection_projects():

    # If only projects from a specific reference are required, get the reference the project is
    # associated with
    output_project = True
    if args.reference:
      project = api_mosaic.get_project(project_info['id'])
      settings = project.get_project_settings()
      reference = settings['reference']
      output_project = True if str(args.reference) == str(reference) else False

    # Only output projects that pass requirements
    if output_project:
      if args.comma_separated_list:
        output_list += str(project_info['id']) + ','
      elif args.ids_only:
        print(project_info['id'])
      elif args.display_raw_output:
        pprint(project_info)
      else:
        print(project_info['name'], ': ', project_info['id'], sep = '')
        if args.display_all:
          print('  nickname: ', project_info['nickname'], sep = '')
          print('  description: ', project_info['description'], sep = '')

  # If a comma separated list is being output, trim the final comma and print
  if args.comma_separated_list:
    print(output_list.rstrip(','))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  display_arguments = groups.display

  # The collection id
  project_arguments.add_argument('--collection_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic collection id to get projects for')

  # Display options
  display_arguments.add_argument('--ids_only', '-io', required = False, action = 'store_true', help = 'Only return project ids')
  display_arguments.add_argument('--display_all', '-da', required = False, action = 'store_true', help = 'Display all project information')
  display_arguments.add_argument('--display_raw_output', '-dr', required = False, action = 'store_true', help = 'Display the raw api output')
  display_arguments.add_argument('--comma_separated_list', '-ol', required = False, action = 'store_true', help = 'Output the project ids as a comma separated list')
  display_arguments.add_argument('--reference', '-r', required = False, metavar = 'string', help = 'Output projects associated with this reference genome')

  return parser.parse_args()

if __name__ == "__main__":
  main()
