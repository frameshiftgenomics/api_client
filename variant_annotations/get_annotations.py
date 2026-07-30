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

  # Get the project settings
  annotation_ids = None
  if args.annotation_ids:
    annotation_ids = args.annotation_ids.split(',')

  # If annotation_version_ids are provided, this will return the annotation ids they are associated with. Therefore
  # annotation_ids cannot also be provided
  version_ids = []
  if args.annotation_version_ids:
    if args.annotation_ids:
      fail('If annotation version ids are provided, annotation ids cannot also be provided')
    version_ids = args.annotation_version_ids.split(',') if ',' in args.annotation_version_ids else [args.annotation_version_ids]

  # Only get the values, if their display was requested
  include_values = 'false'
  if args.show_values:
    fail('Showing values is currently disabled')

    # If a list of annotation ids are not provided, fail. There is too much information to get values for all annotations
    if not args.annotation_ids:
      fail('Annotation ids must be provided to see values')
    args.show_detailed = True
    include_values = 'true'

  # Loop over the annotations
  for annotation in project.get_variant_annotations(annotation_ids = annotation_ids, include_values = include_values, annotation_version_ids = version_ids):

    # If we only want a specific annotation
    if args.name:
      if args.name == annotation['name']:
        if args.show_detailed:
          print_verbose(annotation)
        elif args.ids_only:
          print(annotation['id'])
        else:
          print_simple(annotation)

    # If we only want a specific annotation
    elif args.uid:
      if args.uid == annotation['uid']:
        if args.show_detailed:
          print_verbose(annotation)
        elif args.ids_only:
          print(annotation['id'])
        else:
          print_simple(annotation)

    # If a category is specified, check the value
    elif args.category:
      category = annotation['category']
      if args.category == category:
        if args.show_detailed:
          print_verbose(annotation)
        elif args.ids_only:
          print(annotation['id'])
        else:
          print_simple(annotation)

    # If a privacy class is specified, check the value
    elif args.privacy_level:
      privacy = annotation['privacy_level']
      if args.privacy_level == privacy:
        if args.show_detailed:
          print_verbose(annotation)
        elif args.ids_only:
          print(annotation['id'])
        else:
          print_simple(annotation)

    # Otherwise, print all annotations
    else:

      # If all information, except values were requested
      if args.show_detailed:
        print_verbose(annotation)
      elif args.ids_only:
        print(annotation['id'])
      else:
        print_simple(annotation)

def print_simple(annotation):
  print(annotation['name'], ': ', annotation['id'], sep = '')

def print_verbose(annotation):
  print(annotation['name'], ' (id: ', annotation['id'], ')', sep = '')
  print('    uid: ', annotation['uid'], sep = '')
  print('    original_project: ', annotation['original_project_id'], sep = '')
  print('    versions: ')
  for version in annotation['annotation_versions']:
    print('        ', version['version'], ': ', version['id'], sep = '')
  print('    privacy_level: ', annotation['privacy_level'], sep = '')
  print('    value_type: ', annotation['value_type'], sep = '')
  print('    display_type: ', annotation['display_type'], sep = '')
  print('    severity: ', annotation['severity'], sep = '')
  print('    category: ', annotation['category'], sep = '')

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  optional_arguments = groups.optional
  display_arguments = groups.display

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to get annotations for')

  # If a name is supplied, just show information on the annotation with this name
  optional_arguments.add_argument('--name', '-n', required = False, metavar = 'string', help = 'If an annotation name is provided, information on this annotations will be shown')

  # If an annotation uid is supplied, just show information on the annotation with this name
  optional_arguments.add_argument('--uid', '-u', required = False, metavar = 'string', help = 'If an annotation uid is provided, information on this annotations will be shown')

  # If a list of annotation ids is supplied, only show results for these annotations
  optional_arguments.add_argument('--annotation_ids', '-i', required = False, metavar = 'string', help = 'An optional comman separated list of annotation ids to return')

  # If a list of annotation version ids is supplied, return the annotations they belong to
  optional_arguments.add_argument('--annotation_version_ids', '-vi', required = False, metavar = 'string', help = 'An optional comman separated list of annotation version ids to return their parent annotations')

  # Define a category if only annotations from that category are required
  optional_arguments.add_argument('--category', '-ca', required = False, metavar = 'string', help = 'Only view annotations from this category')
  optional_arguments.add_argument('--privacy_level', '-pl', required = False, metavar = 'string', help = 'Only view annotations from this privacy class: private, semi-public, public')

  # Determine what to display
  display_arguments.add_argument('--ids_only', '-io', required = False, action = 'store_true', help = 'If set, only the annotation ids will be output')
  display_arguments.add_argument('--show_detailed', '-sd', required = False, action = 'store_true', help = 'If set, will display all information except the annotation values')
  display_arguments.add_argument('--show_values', '-sv', required = False, action = 'store_true', help = 'If set, will display all information including the annotation values. Annotation ids must be provided to get values')

  return parser.parse_args()

if __name__ == "__main__":
  main()
