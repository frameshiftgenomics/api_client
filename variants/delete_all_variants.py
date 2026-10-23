import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line and open the Mosaic endpoints
  args = parse_command_line()
  api_mosaic = init(args)

  # Open an api client project object for the defined project
  try:
    project = api_mosaic.get_project(args.project_id)
  except Exception as e:
    fail('Failed to open project. Error was: ' + str(e))

  # A collection's variants come from its projects, so delete from each of those. Any collection
  # containing a project catches up in the background once the project's variants are deleted
  data = project.get_project()
  if data['is_collection']:
    project_ids = data['collection_project_ids']
  else:
    project_ids = [args.project_id]

  # Delete every variant from each project. The variants themselves are not deleted from Mosaic,
  # only the project's genotypes and variant set memberships
  for project_id in project_ids:
    print('Deleting variants from project ', project_id, sep = '')
    try:
      api_mosaic.get_project(project_id).delete_variants()
    except Exception as e:
      fail('Failed to delete variants from project ' + str(project_id) + '. Error was: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()

  # The project to delete the variants from is required
  groups.project.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id (or collection id) to delete all variants from')

  return parser.parse_args()

if __name__ == "__main__":
  main()
