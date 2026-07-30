import os
import json
import math
import glob
import importlib
import sys

from os.path import exists
from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Get the names to change
  names = open(args.annotations_file, 'r')
  update_list = {}
  for line in names.readlines():
    fields = line.rstrip().split(',')
    update_list[fields[0]] = fields[1]

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # Check if this is a collection
  data = project.get_project()
  if data['is_collection']:
    project_ids = data['collection_project_ids']
  else:
    project_ids = [args.project_id]

  # Loop over all the projects (for a collection) and apply the filters
  for project_id in project_ids:
    project = api_mosaic.get_project(project_id)

    # Get all the annotations in the project
    for annotation in project.get_variant_annotations():
      if annotation['name'] in update_list:
        project.put_variant_annotation(annotation['id'], name = update_list[annotation['name']])

# Input options
def parse_command_line():
  parser, _ = base_parser()

  parser.add_argument('--project_id', '-p', required = True, metavar = 'string', help = 'The project id that variants will be uploaded to. Supply the id of a collection and the filters will be applied to all projects in the collection')
  parser.add_argument('--annotations_file', '-f', required = True, metavar = 'string', help = 'A file listing the annotations to change. Each row should be exising,desired')

  return parser.parse_args()

# Process the json file describing the filters to apply
def read_variant_filters_json(variant_filters_json):

  # Check that the file defining the filters exists
  if not exists(variant_filters_json):
    fail('Could not find the json file ' + str(variant_filters_json))

  # The file describing the variant filters should be in json format. Fail if the file is not valid
  try:
    json_file = open(variant_filters_json, 'r')
  except:
    fail('Could not open the json file: ' + str(variant_filters_json))
  try:
    filters_info = json.load(json_file)
  except:
    fail('Could not read contents of json file ' + str(variant_filters_json) + '. Check that this is a valid json')

  # Close the file
  json_file.close()

  # Return the json information
  return filters_info

# Initialise global variables

if __name__ == "__main__":
  main()
