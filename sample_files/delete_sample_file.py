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

  # Delete the file
  project.delete_sample_file(args.sample_id, args.file_id)

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to remove the sample file from')

  # Arguments related to the file to add
  project_arguments.add_argument('--sample_id', '-s', required = True, metavar = 'integer', help = 'The sample id the file is attached to')
  project_arguments.add_argument('--file_id', '-f', required = True, metavar = 'integer', help = 'The file id to be deleted')

  return parser.parse_args()

if __name__ == "__main__":
  main()
