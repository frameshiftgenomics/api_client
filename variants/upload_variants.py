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

  # Check if the project is in any collections and if so, if variants are turned on
  for collection_info in project.get_project()['member_of_collections']:
    collection = api_mosaic.get_project(collection_info['id'])
    info = collection.get_project_settings()
    if info['enable_variant_view']:
      fail('Collection "' + collection.name + '" has variants turned on. Please turn off prior to upload')

  # Check the vcf files
  has_vcfs = False
  for sample in project.get_samples():
    for sample_file in project.get_sample_files(sample['id']):
      if sample_file['type'] == 'vcf':
        if not sample_file['vcf_sample_name']:
          fail('Vcf file attached to the project does not have the vcf_sample_field set. This is required for the upload to complete')
        has_vcfs = True
        break
  if not has_vcfs and not args.sample_map:
    fail('project has no associated vcf files and so a sample map (--sample_map, -s) is required')

  # Set the sample map and notifications
  sample_map = args.sample_map if args.sample_map else None
  notifications = 'false' if args.enable_notifications else 'true'

  # Upload the variants
  try:
    data = project.post_variant_file(args.vcf, upload_type = args.method, disable_successful_notification = notifications, sample_map=sample_map)
  except Exception as e:
    fail('Failed to upload variants. Error: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required
  optional_arguments = groups.optional

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to add variant filters to')

  # Additional arguments
  required_arguments.add_argument('--method', '-m', required = True, metavar = 'string', help = 'The variant upload method: "allele, no-validation, position, raw, sv-no-validation"')
  required_arguments.add_argument('--vcf', '-v', required = True, metavar = 'string', help = 'The vcf file to upload variants from')
  optional_arguments.add_argument('--enable_notifications', '-e', required = False, action = 'store_true', help = 'If set, notifications will be provided. Otherwise, notifications will only be provided for failures')

  # If there is no vcf file attached to the project, we need a file connecting the sample ids to the vcf sample names
  optional_arguments.add_argument('--sample_map', '-s', required = False, metavar = 'string', help = 'The sample map file which is required if there are no vcf files attached to the project')

  return parser.parse_args()

if __name__ == "__main__":
  main()
