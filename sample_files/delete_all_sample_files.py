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

  # Get all of the samples in the project
  samples = {}
  for sample in project.get_samples():
    samples[sample['id']] = sample['name']

  # Get all of the files for each sample
  for sample_id in samples:
    for sample_file in project.get_sample_files(sample_id):

      # Delete the file
      try:
        project.delete_sample_file(sample_id, sample_file['id'])
      except Exception as e:
        fail('Could not delete file. Error: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to remove the sample file from')

  return parser.parse_args()

if __name__ == "__main__":
  main()
