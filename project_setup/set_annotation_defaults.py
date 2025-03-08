import os
import argparse
import json
import sys

from os.path import exists
from pprint import pprint
from sys import path

def main():
  global version

  # Parse the command line
  args = parse_command_line()

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
  api_store = Store(config_file = args.config)
  api_mosaic = Mosaic(config_file = args.config)
  project = api_mosaic.get_project(args.project_id)

  # Get the json file
  json_filename = get_json_filename(project, args)
  json_info = read_json_file(json_filename)

  # Get all the public annotations
  public_annotations = {}
  update_annotations = {}
  for annotation in project.get_variant_annotations_to_import():
    public_annotations[annotation['uid']] = {'id': annotation['id'], \
      'original_project_id': annotation['original_project_id'], \
      'type': annotation['value_type']}

    # Make sure each original project has a list in the update_annotations dictionary
    if annotation['original_project_id'] not in update_annotations:
      update_annotations[annotation['original_project_id']] = []

  # Get all of the annotations
  if 'annotations' not in json_info:
    fail('ERROR: json file does not contain a section titled "annotations" with information on annotations')

  # Loop over all annotations in the json and store information with the original project id of the annotation
  for annotation in json_info['annotations']:
    if annotation in public_annotations:
      category = None
      display_type = None
      severity = None
      value_max_length = None
      value_truncate_type = None

      annotation_id = public_annotations[annotation]['id']
      if 'category' in json_info['annotations'][annotation]:
        category = json_info['annotations'][annotation]['category'] if json_info['annotations'][annotation]['category'] else None
      if 'severity' in json_info['annotations'][annotation]:
        severity = json_info['annotations'][annotation]['severity'] if json_info['annotations'][annotation]['severity'] else None
      if 'display_type' in json_info['annotations'][annotation]:
        display_type = json_info['annotations'][annotation]['display_type'] if json_info['annotations'][annotation]['display_type'] else None
      if 'value_max_length' in json_info['annotations'][annotation]:
        value_max_length = json_info['annotations'][annotation]['value_max_length'] if json_info['annotations'][annotation]['value_max_length'] else None
      if 'value_truncate_type' in json_info['annotations'][annotation]:
        value_truncate_type = json_info['annotations'][annotation]['value_truncate_type'] if json_info['annotations'][annotation]['value_truncate_type'] else None

      # Store the information associated with the project id for the annotation
      original_project_id = public_annotations[annotation]['original_project_id']
      update_annotations[original_project_id].append({'annotation': annotation, \
        'annotation_id': annotation_id, \
        'category': category, \
        'display_type': display_type, \
        'severity': severity, \
        'value_max_length': value_max_length, \
        'value_truncate_type': value_truncate_type})

  # Purge empty lists from update_annotations
  for project_id in list(update_annotations.keys()):
    if len(update_annotations[project_id]) == 0:
      del(update_annotations[project_id])

  # Loop over all original projects with annotations to update and update them
  for project_id in update_annotations:
    project = api_mosaic.get_project(project_id)
    for annotation in update_annotations[project_id]:
      annotation_id = annotation['annotation_id']
      category = annotation['category']
      display_type = annotation['display_type']
      severity = annotation['severity']
      value_max_length = annotation['value_max_length']
      value_truncate_type = annotation['value_truncate_type']
      project.put_variant_annotation(annotation_id, display_type = display_type, severity = severity, category = category, value_truncate_type = value_truncate_type, value_max_length = value_max_length)

# Input options
def parse_command_line():
  global version
  parser = argparse.ArgumentParser(description='Process the command line')

  # Required arguments
  parser.add_argument('--config', '-c', required = True, metavar = 'string', help = 'The config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The directory where the Python api wrapper lives')

  # Optional pipeline arguments
  parser.add_argument('--json', '-j', required = False, metavar = 'string', help = 'The json file describing the project defaults')
  parser.add_argument('--instance', '-i', required = False, metavar = 'string', help = 'The mosaic instance. Will be used to build the json file name')
  parser.add_argument('--json_path', '-s', required = False, metavar = 'string', help = 'The path to the json file. Not required if --json is set, but will be used to build the json filename')

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  return parser.parse_args()

# Build the json filename
def get_json_filename(project, args):

  # Build the name of the json file
  if args.json:
    json_filename = args.json
  else:
    if not args.json_path or not args.instance:
      fail('No json file was supplied (--json, -j). If no json is supplied, both --json_path (-s) and --instance (-i) must be set so that the filename can be constructed')
    if not args.json_path.endswith('/'):
      args.json_path = args.json_path + '/'

    # Get the project reference
    data = project.get_project_settings()
    reference = data['reference']
    json_filename = args.json_path + 'project_defaults_' + str(args.instance) + '_' + str(reference) + '.json'

  return json_filename
  
# Check that the json containing the required defaults exists and read in the information
def read_json_file(json_filename):
  try:
    json_file = open(json_filename, 'r')
  except:
    fail('Could not open the json file: ' + str(json_filename))
  try:
    json_info = json.load(json_file)
  except:
    fail('Could not read contents of json file ' + str(json_filename) + '. Check that this is a valid json')
  json_file.close()
 
  return json_info

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

# Throw a warning
def warning(message):
  print('WARNING: ', message, sep = '')

# Initialise global variables

if __name__ == "__main__":
  main()
