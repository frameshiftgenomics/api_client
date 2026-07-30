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

  # Get the sample attributes and find the id of the Relation attribute
  relation_values = None
  for attribute in project.get_sample_attributes(include_values = 'true'):
    if attribute['name'] == 'Relation':
      relation_values = {}
      for value in attribute['values']:
        relation_values[value['sample_id']] = value['value']
      break
  if not relation_values:
    fail('The Relation sample attribute could not be found in the project')

  # Delete the file
  samples = project.get_samples()
  for sample in samples:
    if args.relation:
      if relation_values[sample['id']] == args.relation:
        if args.ids_only:
          print(sample['id'])
        else:
          print(sample['name'], sample['id'], relation_values[sample['id']], sep = '\t')
    else:

      if args.ids_only:
        print(sample['id'])
      else:
        print(sample['name'], sample['id'], relation_values[sample['id']], sep = '\t')

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  optional_arguments = groups.optional
  display_arguments = groups.display

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # Which relation to look for
  optional_arguments.add_argument('--relation', '-r', required = False, metavar = 'string', help = 'The name of the relation to find, e.g. proband, or mother. If not set, all samples will be returned')

  # Output ids only
  display_arguments.add_argument('--ids_only', '-io', required = False, action = 'store_true', help = 'Only output sample ids')

  return parser.parse_args()

if __name__ == "__main__":
  main()
