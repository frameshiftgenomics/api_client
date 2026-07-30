import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # Loop over all samples in the project
  for sample in project.get_samples():
    no_files = 0
    for sample_file in project.get_sample_files(sample['id']):
      no_files += 1

      # If the file does not have a type, throw a warning
      if not sample_file['type']:
        print('WARNING: file ', sample_file['id'], ' (', sample_file['name'], ') has no type', sep = '')

      # If the file is a vcf or tbi file, check that the vcf_sample_name is set
      if sample_file['type'] == 'vcf' or sample_file['type'] == 'tbi':
        if not sample_file['vcf_sample_name']:
          print('WARNING: file ', sample_file['id'], ' (', sample_file['name'], ') does not have vcf_sample_name set', sep = '')
        elif sample_file['vcf_sample_name'] != sample['name']:
          print('WARNING: file ', sample_file['id'], ' (', sample_file['name'], ') has a different vcf_sample_name (', sample_file['vcf_sample_name'], ') to the sample name (', sample['name'], ')', sep = '')

    # If the sample has no files attached, throw a warning
    if no_files == 0:
      print('WARNING: sample ', sample, ' (', sample['id'], ') has no associated files', sep = '')
      

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The project id
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  return parser.parse_args()

if __name__ == "__main__":
  main()
