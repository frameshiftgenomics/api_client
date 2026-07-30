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

  # Apply the template
  data = project.patch_project(args.template_id)

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # The project id of the template to apply
  parser.add_argument('--template_id', '-t', required = True, metavar = 'integer', help = 'The Mosaic project id of the template to apply')

  return parser.parse_args()

if __name__ == "__main__":
  main()
