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

  # Upload the ped file
  create_new_samples = 'true' if not args.no_new_samples else 'false'
  data = project.post_upload_pedigree(file_path = args.pedigree_file, create_new_samples = create_new_samples)

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to add variant filters to')

  # Additional arguments
  parser.add_argument('--pedigree_file', '-f', required = True, metavar = 'string', help = 'The ped file to upload')
  parser.add_argument('--no_new_samples', '-n', required = False, action = 'store_true', help = 'If set, no new samples will be created')

  return parser.parse_args()

if __name__ == "__main__":
  main()
