import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line and open the Mosaic endpoints
  args = parse_command_line()
  api_mosaic = init(args)

  # The route only accepts a vcf.gz or a bcf
  if not args.vcf.endswith('.vcf.gz') and not args.vcf.endswith('.bcf'):
    fail('The file to delete variants from must be a vcf.gz or a bcf')
  if not os.path.exists(args.vcf):
    fail('File "' + args.vcf + '" does not exist')

  # Open an api client project object for the defined project
  try:
    project = api_mosaic.get_project(args.project_id)
  except Exception as e:
    fail('Failed to open project. Error was: ' + str(e))

  # Delete every variant in the vcf from the project. The variants themselves are not deleted
  # from Mosaic, only the project's genotypes and variant set memberships
  try:
    data = project.delete_variants_by_vcf(args.vcf)
  except Exception as e:
    fail('Failed to delete variants. Error was: ' + str(e))

  # Output the summary the route returns
  if args.raw_output:
    pprint(data)
  else:
    print('variants deleted from the project: ', data['deleted_count'], sep = '')
    print('variants in the file, but not in the project: ', data['not_in_project_count'], sep = '')
    print('variants in the file, but not in Mosaic: ', len(data['not_found']), sep = '')
    if args.display_all_information:
      for variant in data['not_found']:
        print('   ', variant, sep = '')

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required
  display_arguments = groups.display

  # The project to delete the variants from is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to delete variants from')

  # The vcf listing the variants to delete
  required_arguments.add_argument('--vcf', '-v', required = True, metavar = 'string', help = 'The vcf.gz or bcf file listing the variants to delete from the project')

  # Output options
  display_arguments.add_argument('--raw_output', '-ro', required = False, action = 'store_true', help = 'If set, output the raw response from the API')
  display_arguments.add_argument('--display_all_information', '-da', required = False, action = 'store_true', help = 'If set, list the variants in the file that are not in Mosaic')

  return parser.parse_args()

if __name__ == "__main__":
  main()
