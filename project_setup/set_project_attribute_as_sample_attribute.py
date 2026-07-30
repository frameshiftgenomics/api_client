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

  # Open an api client project object for the defined project
  try:
    project = api_mosaic.get_project(args.project_id)
  except Exception as e:
    fail('failed to open project. Error was: ' + str(e))

  # Check if this is a collection
  try:
    data = project.get_project()
  except Exception as e: 
    fail('failed to get project information. Error was: ' + str(e))
  if data['is_collection']:
    project_ids = []
    for sub_project in data['collection_projects']:
      project_ids.append(sub_project['child_project_id'])
  else:
    project_ids = [args.project_id]

  # Loop over all the projects (for a collection) and apply the filters
  for project_id in project_ids:
    project = api_mosaic.get_project(project_id)
    print('Updating project ', project.name, ' (id:', project_id,')', sep = '')

    # Get the value of the project attribute
    value = False
    for project_attribute in project.get_project_attributes():
      if int(project_attribute['id']) == int(args.project_attribute_id):
        for attribute_value in project_attribute['values']:
          if int(attribute_value['project_id']) == int(project_id):
            value = attribute_value['value']
            break
    if not value:
      print('   The requested project attribute was not set for this project')

    # Import the sample attribute
    else: 
      try:
        data = project.post_import_sample_attribute(args.sample_attribute_id)
      except:
        pass

      for sample_info in project.get_samples():

        # PUT the value into the sample attribute and POST if this fails
        try:
          data = project.post_sample_attribute_value(sample_info['id'], args.sample_attribute_id, value)
        except:
          data = project.put_sample_attribute_value(sample_info['id'], args.sample_attribute_id, value)
  
# Input options
def parse_command_line():
  global version
  parser, _ = base_parser()

  # The project or collection id to add samplt attribute to
  parser.add_argument('--project_id', '-p', required = True, metavar = 'string', help = 'The project id that variants will be uploaded to')

  # The project attribute id to use for the sample attribute
  parser.add_argument('--project_attribute_id', '-r', required = True, metavar = 'string', help = 'The project attribute id whoe value will be used to set the sample attribute it')

  # The sample attribute id to set the value for
  parser.add_argument('--sample_attribute_id', '-s', required = True, metavar = 'string', help = 'The sample attribute id to set the value for')

  return parser.parse_args()

# Initialise global variables

if __name__ == "__main__":
  main()
