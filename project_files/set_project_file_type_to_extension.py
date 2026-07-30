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

  # Check if this is a collection
  data = project.get_project()
  if data['is_collection']:
    project_ids = []
    for project_id in data['collection_project_ids']:
      project_ids.append(project_id)
  else:
    project_ids = [args.project_id]

  # Loop over all projects
  for project_id in project_ids:
    project = api_mosaic.get_project(project_id)
    print('Checking project: ', project.name, sep = '')

    # Get all project files
    for project_file in project.get_project_files():
      extension = project_file['name'].rsplit('.')[-1]
      if str(extension) == str(args.extension):
        project.put_project_file(project_file['id'], file_type = extension)

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The project id
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id')

  # Convert files with this extension
  parser.add_argument('--extension', '-e', required = True, metavar = 'string', help = 'The extension to set. Files that have this extension will have their type set to this')

  return parser.parse_args()

if __name__ == "__main__":
  main()
