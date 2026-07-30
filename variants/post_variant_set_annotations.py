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

  # Update the variant annotation ids in the dashboard variant table
  annotation_version_ids = []
  for annotation_version_id in args.annotation_version_ids.split(','):
    annotation_version_ids.append(str(annotation_version_id))
  data = project.post_variant_set_annotations(args.variant_set_id, annotation_version_ids)

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # The variant set id to update the display of
  parser.add_argument('--variant_set_id', '-v', required = True, metavar = 'integer', help = 'The Mosaic variant set id to update')

  # The annotation ids to include in the table for pinned variant sets
  parser.add_argument('--annotation_version_ids', '-i', required = True, metavar = 'string', help = 'A comma separated list of annotation version ids to include in the pinned variant table')

  return parser.parse_args()

if __name__ == "__main__":
  main()
