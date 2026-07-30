import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():
  global api_mosaic
  global allowed_references
  global system_projects

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

#  # If attribute filters are set, turn them into a json
  attribute_filters = []
#  if args.attribute_filters:
#
#    # Get each filter, then break into uid, value_type and value
#    for attribute_filter in args.attribute_filters.split(','):
#      values = attribute_filter.split(':')
#      attribute_filters.append({'uid': values[0], 'value_type': values[1], 'values': values[2].split('|')})

  if args.reference:
    if args.reference not in allowed_references:
      fail('Unknown reference genome: ' + str(args.reference))

  # If only collections are to be output, collections need to be included
  if args.only_collections:
    args.include_collections = True

  # Get the list of project ids to return
  all_project_ids = None
  if args.project_ids:
    all_project_ids = args.project_ids.split(',') if ',' in args.project_ids else [args.project_ids]

  # Loop through the projects list 100 at at time
  if all_project_ids:
    for i in range(0, len(all_project_ids), 100):
      project_ids = all_project_ids[i:i + 100]
      process_projects(args, project_ids, attribute_filters)
  else:
    process_projects(args, None, attribute_filters)

# Process the projects
def process_projects(args, project_ids, attribute_filters):

  # Get all the available projects
  for project_info in api_mosaic.get_projects(search = args.search, only_collections = args.only_collections, project_ids = project_ids, attribute_filters = attribute_filters):
    display = True
    if args.reference:
      if project_info['reference'] != args.reference:
        display = False

    # Ignore template projects unless told otherwise
    if project_info['is_template']:
      if not args.include_templates:
        display = False

    # Ignore collections unless told otherwise
    if project_info['is_collection']:
      if not args.include_collections:
        display = False

    # By default ignore system projects. This is the Public Attributes, Mosaic <REF> Globals projects
    if project_info['name'] in system_projects:
      if not args.include_system_projects:
        display = False

    # Only output projects with variants
    if args.output_projects_with_variants:
      if project_info['variant_count'] == 0:
        display = False

    # Write out information
    if display:
      if args.raw_output:
        pprint(project_info)
      elif args.output_projects_with_variants:
        print(project_info['id'], ':', project_info['variant_count'], sep = '')
      elif args.output_ids_only:
        print(project_info['id'], sep = '')
      elif args.display_all:
        print(project_info['name'], ': ', project_info['id'], sep = '')
        print('  task count: ', project_info['task_count'], sep = '')
        print('  variant count: ', project_info['variant_count'], sep = '')
      else:
        print(project_info['name'], ': ', project_info['id'], sep = '')

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  optional_arguments = groups.optional
  display_arguments = groups.display

  # Limit search to specific projects
  project_arguments.add_argument('--project_ids', '-p', required = False, metavar = 'string', help = 'A comma separate list of project ids to get information for')

  # Filter projects based on attributes
  #optional_arguments.add_argument('--attribute_filters', '-f', required = False, metavar = 'string', help = 'A comma separated list of attributes to filter on, in the format uid:value_type:value1|value2 etc')

  # Only output project ids, or exclude specific projects
  display_arguments.add_argument('--output_ids_only', '-o', required = False, action = 'store_true', help = 'If set, only the project ids will be output')
  display_arguments.add_argument('--include_templates', '-t', required = False, action = 'store_true', help = 'By default, template projects will NOT be included in the output. This will include them')
  display_arguments.add_argument('--include_collections', '-i', required = False, action = 'store_true', help = 'By default, collections will NOT be included in the output. This will include them')
  display_arguments.add_argument('--include_system_projects', '-n', required = False, action = 'store_true', help = 'By default, system projects (Public Attribute, Globals) will NOT be included in the output. This willi include them')

  # Only output projects of a given reference
  display_arguments.add_argument('--reference', '-r', required = False, metavar = 'string', help = 'Only output projects with the specified reference')

  # Only output collections
  display_arguments.add_argument('--only_collections', '-oc', required = False, action = 'store_true', help = 'If set, only return collections')

  # Display the raw output
  display_arguments.add_argument('--raw_output', '-ro', required = False, action = 'store_true', help = 'Output an unformatted dump of all information')

  # Display the raw output
  display_arguments.add_argument('--display_all', '-da', required = False, action = 'store_true', help = 'Output all information in a formatted output')

  # Output projects with variants
  display_arguments.add_argument('--output_projects_with_variants', '-v', required = False, action = 'store_true', help = 'Only output information on projects with variants')

  # Query params
  display_arguments.add_argument('--search', '-s', required = False, metavar = 'string', help = 'Term to search on')

  return parser.parse_args()

api_mosaic = None

allowed_references = []
allowed_references.append('GRCh37')
allowed_references.append('GRCh38')

system_projects = []
system_projects.append('Public Attributes')
system_projects.append('Mosaic Globals')
system_projects.append('Mosaic GRCh37 Globals')
system_projects.append('Mosaic GRCh38 Globals')

if __name__ == "__main__":
  main()
