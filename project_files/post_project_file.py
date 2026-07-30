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

  # Post the file
  endpoint_url = args.endpoint_url if args.endpoint_url else None
  project.post_project_file(name = args.name, file_type = args.file_type, uri = args.uri, reference = args.reference, endpoint_url = endpoint_url)

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # Arguments related to the file to add
  parser.add_argument('--name', '-n', required = True, metavar = 'string', help = 'The name of the file being attached')
  parser.add_argument('--file_type', '-t', required = True, metavar = 'string', help = 'The file type of the file being attached')
  parser.add_argument('--uri', '-u', required = True, metavar = 'string', help = 'The uri of the file being attached')
  parser.add_argument('--reference', '-r', required = True, metavar = 'string', help = 'The project reference')

  # Optional arguments
  parser.add_argument('--endpoint_url', '-d', required = False, metavar = 'string', help = 'The endpoint url of the file being attached')

  return parser.parse_args()

if __name__ == "__main__":
  main()
