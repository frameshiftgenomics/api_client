import os
import json
import sys

from os.path import exists
from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, warning, fail

def main():
  global version

  # Parse the command line
  args = parseCommandLine()

  api_mosaic = init(args)

  # Check that the supplied project id is for a collection
  collection = api_mosaic.get_project(args.project_id)
  data = collection.get_project()
  if not data['is_collection']:
    fail('Supplied project id (' + args.project_id + ') is for a project, not a collection')

  # Loop over all projects in the collection
  for project_info in collection.get_collection_projects():
    project_id = project_info['id']
    print('Applying template to project ' + project_info['name'] + ', id: ' + str(project_id))

    # Open the project and apply the template
    project = api_mosaic.get_project(project_id)
    data = project.patch_project(args.template_id)

# Input options
def parseCommandLine():
  parser, _ = base_parser()

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # The project id of the template project
  parser.add_argument('--template_id', '-t', required = True, metavar = 'integer', help = 'The Mosaic project id of the template project')

  return parser.parse_args()

# Throw a warning
def warning(message):
  print('WARNING: ', message, sep = '')

# Initialise global variables

if __name__ == "__main__":
  main()
