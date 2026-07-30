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
  project.delete_project_file(args.file_id)

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The project id
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project')

  # Arguments related to the file to add
  parser.add_argument('--file_id', '-f', required = True, metavar = 'integer', help = 'The file id to be deleted')

  return parser.parse_args()

if __name__ == "__main__":
  main()
