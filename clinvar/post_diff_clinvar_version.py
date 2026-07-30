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
    fail('failed to open project. Error was: ' + str(e))

  # Check the name of the project
  if project.name != 'Mosaic GRCh37 Globals' and project.name != 'Mosaic GRCh38 Globals':
    fail('ClinVar version must be added to a Mosaic Globals project, not "' + project.name + '"')

  # Check that the ClinVar version version is a string of 8 integers
  if len(args.clinvar_version_a) != 8:
    fail('The original ClinVar version must be a string of 8 integers in the format YYYYMMDD')
  if len(args.clinvar_version_b) != 8:
    fail('The new ClinVar version must be a string of 8 integers in the format YYYYMMDD')
    
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

  # Check that the requested versions exist
  if args.clinvar_version_a not in annotation_versions:
    fail('The original ClinVar version (' + str(args.clinvar_version_a) + ') does not exist')
  if args.clinvar_version_b not in annotation_versions:
    fail('The new ClinVar version (' + str(args.clinvar_version_b) + ') does not exist')
  version_a_id = annotation_versions[args.clinvar_version_a]
  version_b_id = annotation_versions[args.clinvar_version_b]

  # Get the project ids to of the projects to check
  if args.project_ids_to_check:
    if ',' in args.project_ids_to_check:
      project_ids = args.project_ids_to_check.split(',')
    else:
      project_ids = [args.project_ids_to_check]

  # Generate a list of email addresses to send notifications to
  emails = None
  if args.emails:
    args.emails = args.emails.rstrip('"') if args.emails.endswith('"') else args.emails
    args.emails = args.emails.lstrip('"') if args.emails.startswith('"') else args.emails
    emails = args.emails.split(',') if ',' in args.emails else [args.emails]

  # If an allele frequency is given, set the annotation filters
  annotation_filters = []
  if args.gnomad_af:
    if ',' not in args.gnomad_af:
      fail('gnomAD_AF filter must be in the form "uid,value"')
    gnomad = args.gnomad_af.split(',')

    # Get the annotation from the uid
    uid = gnomad[0]
    value = gnomad[1]

    #[{"annotation_version_id": "23", "uid" : "floattest_736a1100", "value_type": "float", "include_nulls": false, "min": "1", "max": "10"}]
    gnomad_af_uid = False
    for annotation in project.get_variant_annotations():
      if str(annotation['uid']) == uid:
        gnomad_af_uid = uid

        # Get the annotation version id
        if annotation['latest_annotation_version_id']:
          version_id = annotation['latest_annotation_version_id']
        elif len(annotation['annotation_versions']) == 1:
          version_id = annotation['annotation_versions'][0]['id']
        else:
          fail('Unable to find the annotation version id for gnomAD AF')
        break

    # Fail if the uid was not found
    if not gnomad_af_uid:
      fail('the gnomAD AF annotation with the given uid was not found: ' + uid)
    annotation_filters.append({'annotation_version_id': version_id, 'uid': str(gnomad_af_uid), 'value_type': 'float', 'max': str(value), 'include_nulls': 'true'})

  # Perform the diff
  generate_tasks = 'false' if args.disable_tasks else None
  include_hpo_ancestors = 'true' if args.include_hpo_ancestors else 'false'
  project.post_diff_clinvar_version(version_a = args.clinvar_version_a, version_b = args.clinvar_version_b, project_ids = project_ids, generate_tasks = generate_tasks, emails = emails, annotation_filters = annotation_filters, include_hpo_ancestors = include_hpo_ancestors)

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required
  optional_arguments = groups.optional

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # The ClinVar versions to diff
  required_arguments.add_argument('--clinvar_version_a', '-v', required = True, metavar = 'string', help = 'The original ClinVar version in the format YYYYMMDD')
  required_arguments.add_argument('--clinvar_version_b', '-b', required = True, metavar = 'string', help = 'The new ClinVar version in the format YYYYMMDD')

  # The gnomAD allele frequency to filter on, this should be in the form "uid,value"
  optional_arguments.add_argument('--gnomad_af', '-g', required = False, metavar = 'string', help = 'The max gnomAD allele frequency to filter out common variants')

  # A list of project ids can be supplied as a comma separated list
  optional_arguments.add_argument('--project_ids_to_check', '-i', required = True, metavar = 'string', help = 'A comma separated list of project ids to check for updated ClinVar variants')

  # A list of email address to notify about the update
  optional_arguments.add_argument('--emails', '-e', required = False, metavar = 'string', help = 'A comma separated list of email address to send notifications to')

  # Do not create any tasks in Mosaic. By default, create tasks
  optional_arguments.add_argument('--disable_tasks', '-d', required = False, action = 'store_true', help = 'By default, tasks will be created for all ClinVar variants to review. This flag will disable task creation')

  # Use the updated HPO terms including ancestry
  optional_arguments.add_argument('--include_hpo_ancestors', '-ih', required = False, action = 'store_true', help = 'Set to include HPO ancestry terms')

  return parser.parse_args()

if __name__ == "__main__":
  main()
