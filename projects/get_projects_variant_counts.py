import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():
  global allowed_references
  global system_projects

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  if args.reference:
    if args.reference not in allowed_references:
      fail('Unknown reference genome: ' + str(args.reference))

  # Get all the available projects
  for project_info in api_mosaic.get_projects(search = args.search):
    display = True
    if args.reference:
      display = False
    variant_count = 0 if not project_info['variant_count'] else project_info['variant_count']
    if args.min_variants:
      if int(variant_count) < int(args.min_variants):
        display = False
    if args.max_variants:
      if int(variant_count) > int(args.max_variants):
        display = False

    # Ignore template
    if project_info['is_template']:
      display = False

    # Ignore collections
    if project_info['is_collection']:
      display = False

    # Ignore system projects. This is the Public Attributes, Mosaic <REF> Globals projects
    if project_info['name'] in system_projects:
      display = False

    # Write out information
    if display:
      print(project_info['name'], project_info['variant_count'])

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  optional_arguments = groups.optional
  display_arguments = groups.display

  # Only output projects of a given reference
  project_arguments.add_argument('--reference', '-r', required = False, metavar = 'string', help = 'Only output projects with the specified reference')

  # Query params
  optional_arguments.add_argument('--search', '-s', required = False, metavar = 'string', help = 'Term to search on')

  # Display params
  display_arguments.add_argument('--min_variants', '-min', required = False, metavar = 'integer', help = 'Only output projects with a minimum of this number of variants')
  display_arguments.add_argument('--max_variants', '-max', required = False, metavar = 'integer', help = 'Only output projects with a maximum of this number of variants')

  return parser.parse_args()

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
