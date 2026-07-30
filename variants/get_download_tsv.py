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
  try:
    project = api_mosaic.get_project(args.project_id)
  except Exception as e:
    fail('failed to open project. Error was: ' + str(e))

  # Get the variants
  try:
    with open(args.tsv, "wb") as f:
      f.write(project.get_download_variants_tsv())
  except Exception as e:
    fail('failed to get variants. Error was: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to download variants for')

  # The output file
  required_arguments.add_argument('--tsv', '-t', required = True, metavar = 'string', help = 'The output tsv file')

  return parser.parse_args()

if __name__ == "__main__":
  main()
