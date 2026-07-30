import os
import sys

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
    fail('Failed to open project. Error was: ' + str(e))

  # Get all of the sample files
  try:
    has_url = project.get_sample_file_url(args.file_id)
    print('File is valid')
  except Exception as e:
    has_url = False
    if args.write_error:
      print('File is not valid. Error was: ', str(e), sep = '')
    else:
      print('File is not valid')

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required
  display_arguments = groups.display

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # Arguments related to the file to add
  required_arguments.add_argument('--file_id', '-f', required = True, metavar = 'integer', help = 'The file id to get the url of')

  # Write out the error if required
  display_arguments.add_argument('--write_error', '-we', required = False, action = 'store_true', help = 'Write out the error if the file is not valid')

  return parser.parse_args()

if __name__ == "__main__":
  main()
