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
    fail('Failed to open project. Error was: ' + str(e))

  # Turn the provided attribute ids into an array
  sample_attribute_ids = args.sample_attribute_ids.split(',') if ',' in args.sample_attribute_ids else [args.sample_attribute_ids]

  # Update the project settings
  try:
    project.put_project_settings(selected_sample_attribute_column_ids = sample_attribute_ids)
  except Exception as e:
    fail('Unable to update the samples attribute table defaults. Error was: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')
  project_arguments.add_argument('--sample_attribute_ids', '-s', required = True, metavar = 'string', help = 'An ordered, comma separated list of the sample attribute ids to set as the defaults for the sample attribute table')

  return parser.parse_args()

if __name__ == "__main__":
  main()
