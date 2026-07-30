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

  # Check the supplied reference
  allowed_references = ['grch37', 'grch38']
  if args.reference not in allowed_references:
    fail('Unknown reference')

  # Get all annotations with this reference to remove
  for annotation in project.get_variant_annotations():
    if args.reference in annotation['uid']:
      project.delete_variant_annotation(annotation['id'])

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to get annotations for')

  # The reference to remove
  parser.add_argument('--reference', '-r', required = True, metavar = 'string', help = 'The reference to remove annotations for: grch37, grch38')

  return parser.parse_args()

if __name__ == "__main__":
  main()
