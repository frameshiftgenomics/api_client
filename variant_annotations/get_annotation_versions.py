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
    fail('Unable to open project with the given id. The project id must be a valid integer')

  # Check for mututally exclusive options
  flag_list = (args.default, args.default_redirect, args.latest, args.latest_redirect)
  if sum(flag_list) > 1:
    fail('multiple flags to get default, latest etc are set. These flags are mutually exclusive')

  # Get the annotation version information
  for annotation_version in project.get_variant_annotation_versions(args.annotation_id):
    if args.default:
      if annotation_version['version'] == 'default':
        if args.ids_only:
          print(annotation_version['id'])
        else:
          print(annotation_version['version'], ': ', annotation_version['id'], ', redirects to: ', annotation_version['redirect_to_id'], sep = '')
    elif args.default_redirect:
      if annotation_version['version'] == 'default':
        print(annotation_version['redirect_to_id'])
    elif args.latest:
      if annotation_version['version'] == 'Latest':
        if args.ids_only:
          print(annotation_version['id'])
        else:
          print(annotation_version['version'], ': ', annotation_version['id'], ', redirects to: ', annotation_version['redirect_to_id'], sep = '')
    elif args.latest_redirect:
      if annotation_version['version'] == 'Latest':
        print(annotation_version['redirect_to_id'])
    else:
      if annotation_version['version'] == 'default' or annotation_version['version'] == 'Latest':
        if args.ids_only:
          print(annotation_version['id'])
        else:
          print(annotation_version['version'], ': ', annotation_version['id'], ', redirects to: ', annotation_version['redirect_to_id'], sep = '')
      else:
        if args.ids_only:
          print(annotation_version['id'])
        else:
          print(annotation_version['version'], ': ', annotation_version['id'], sep = '')

# Input options
def parse_command_line():
  parser, groups = base_parser()
  required_arguments = groups.required
  optional_arguments = groups.optional

  # The project id to which the filter is to be added is required
  required_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to get annotations for')

  # Get the annotation id
  required_arguments.add_argument('--annotation_id', '-i', required = True, metavar = 'integer', help = 'The annotation id to get')

  # Optional arguments
  optional_arguments.add_argument('--default', '-d', required = False, action = 'store_true', help = 'Get the id of the default version')
  optional_arguments.add_argument('--default_redirect', '-dr', required = False, action = 'store_true', help = 'Get the id of the version that default points to')
  optional_arguments.add_argument('--latest', '-l', required = False, action = 'store_true', help = 'Get the id of the latest version')
  optional_arguments.add_argument('--latest_redirect', '-lr', required = False, action = 'store_true', help = 'Get the id of the version that latest points to')

  # Display arguments
  optional_arguments.add_argument('--ids_only', '-io', required = False, action = 'store_true', help = 'Only output the annotation id')

  return parser.parse_args()

if __name__ == "__main__":
  main()
