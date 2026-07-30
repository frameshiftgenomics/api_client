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

  # Check the name of the project
  if project.name != 'Mosaic GRCh37 Globals' and project.name != 'Mosaic GRCh38 Globals':
    fail('ClinVar version must be added to a Mosaic Globals project, not "' + project.name + '"')

  # Check that the ClinVar version version is a string of 8 integers
  if len(args.clinvar_version) != 8:
    fail('ClinVar version must be a string of 8 integers in the format YYYYMMDD')
    
  # Get the reference of the project
  reference = project.get_project_settings()['reference']

  # Find the ClinVar annotation
  clinvar_annotation_name = 'ClinVar Significance ' + str(reference)
  annotation_id = None
  for annotation in project.get_variant_annotations():
    if annotation['name'] == clinvar_annotation_name:
      annotation_id = annotation['id']

  # Fail if the ClinVar annotation couldn't be found
  if not annotation_id:
    fail('Could not find an annotation called ' + clinvar_annotation_name)

  # Get the available annotation versions
  annotation_versions = {}
  for annotation_version in project.get_variant_annotation_versions(annotation_id):
    annotation_versions[annotation_version['version']] = annotation_version['id']

  # Check if a version of the requested name already exists
  version_exists = True if args.clinvar_version in annotation_versions else False

  # Add the ClinVar version if it doesn't already exist
  if not version_exists:
    project.post_add_clinvar_version(version = args.clinvar_version)

    # Update the version ids with the added version
    for annotation_version in project.get_variant_annotation_versions(annotation_id):
      annotation_versions[annotation_version['version']] = annotation_version['id']

  # Set the version as the latest unless specifically told not to
  #if not args.disable_latest:
  #  annotation_version_id = annotation_versions[args.clinvar_version]
  #  project.put_variant_annotation(annotation_id, latest_version_id = annotation_version_id)

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # The ClinVar version to add
  parser.add_argument('--clinvar_version', '-v', required = True, metavar = 'string', help = 'The ClinVar version in the format YYYYMMDD')

  # Do not set version as latest
  parser.add_argument('--disable_latest', '-l', required = False, action = 'store_true', help = 'By default, the added version will be set as the latest. This will ensure the added version is NOT set as Latest')

  return parser.parse_args()

if __name__ == "__main__":
  main()
