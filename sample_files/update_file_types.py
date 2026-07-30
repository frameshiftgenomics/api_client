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

  # Get the sample ids
  for sample in project.get_samples():

    # Loop over all sample files for each sample
    for sample_file in project.get_sample_files(sample['id']):
      if sample_file['name'].endswith(args.extension):
        project.put_sample_file(sample['id'], sample_file['id'], file_type = args.file_type)

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The project id
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # The file extension to modify
  parser.add_argument('--extension', '-e', required = True, metavar = 'string', help = 'The extension of the files to update the file type')

  # The file type to apply to files with the given extension
  parser.add_argument('--file_type', '-t', required = True, metavar = 'string', help = 'The file type to apply')

  return parser.parse_args()

if __name__ == "__main__":
  main()
