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

  # Check that the annotation exists
  try:
    for annotation_version in project.get_variant_annotation_versions(args.annotation_id):

      # If the annotation already has a version with the same name, fail if there isn't a request to
      # overwrite
      if str(annotation_version['version']) == str(args.version_name):
        if not args.overwrite_version:
          fail('Annotation version with the name ' + str(args.version_name) + ' already exists. Set --overwrite_version (-o) to overwrite')
        else:

          # Delete the annotation version
          try:
            project.delete_variant_annotation_version(args.annotation_id, annotation_version['id'])
          except Exception as e:
            fail('Failed to delete existing annotation version. Error was: ' + str(e))
          break
  except Exception as e:
    fail('Could not get annotation. Check that this annotation exists in the specified project. Error was: ' + str(e))

  # Create the new annotation version
  try:
    project.post_create_annotation_version(args.annotation_id, args.version_name)
  except Exception as e:
    fail('Failed to add annotation. Error was: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required
  optional_arguments = groups.optional

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # Information about the annotation being created
  required_arguments.add_argument('--annotation_id', '-i', required = True, metavar = 'integer', help = 'The id of the annotation to create a new version for')
  required_arguments.add_argument('--version_name', '-n', required = True, metavar = 'string', help = 'The name of the annotation version to create')

  # Optional arguments
  optional_arguments.add_argument('--overwrite_version', '-o', required = False, action = 'store_true', help = 'If set, existing annotation versions with the same name will be removed')

  return parser.parse_args()

if __name__ == "__main__":
  main()
