import os
import argparse
import json
import math
import glob
import importlib
import sys

from os.path import exists
from pprint import pprint
from sys import path

def main():

  # Parse the command line
  args = parseCommandLine()

  # If the api_client path was not specified, get it from the script path
  if not args.api_client:
    try:
      args.api_client = os.path.dirname(os.path.realpath(__file__)).split('api_client')[0] + str('api_client')
    except:
      fail('Could not get the api_client path from the command. Please specify using --api_client / -a')

  # Import the api client
  path.append(args.api_client)
  try:
    from mosaic import Mosaic, Project, Store
  except:
    fail('Cannot find mosaic. Please set the --api_client / -a argument')
  api_store = Store(config_file = args.client_config)
  api_mosaic = Mosaic(config_file = args.client_config)

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # Check if this is a collection
  data = project.get_project()
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
def parseCommandLine():
  global version
  parser = argparse.ArgumentParser(description='Process the command line')

  # Required arguments
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

  # The project or collection id to add samplt attribute to
  parser.add_argument('--project_id', '-p', required = True, metavar = 'string', help = 'The project id that variants will be uploaded to')

  # The project attribute id to use for the sample attribute
  parser.add_argument('--project_attribute_id', '-r', required = True, metavar = 'string', help = 'The project attribute id whoe value will be used to set the sample attribute it')

  # The sample attribute id to set the value for
  parser.add_argument('--sample_attribute_id', '-s', required = True, metavar = 'string', help = 'The sample attribute id to set the value for')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print(message, sep = '')
  exit(1)

# Initialise global variables

if __name__ == "__main__":
  main()
