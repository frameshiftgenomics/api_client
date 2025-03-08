import os
import argparse
import json
import sys

from datetime import date
from os.path import exists
from sys import path

def main():

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
  store = Store(config_file = args.config)
  mosaic = Mosaic(config_file = args.config)
  project = mosaic.get_project(args.project_id)

  # Read the Mosaic json and validate its contents
  annotations_info = read_annotations_json(args.json)

  # Get all of the private annotations
  for annotation in project.get_variant_annotations():
    if annotation['privacy_level'] == 'private':
      if annotation['name'] in annotations_info['annotations']:
        category = annotations_info['annotations'][annotation['name']]['category']
        display_type = annotations_info['annotations'][annotation['name']]['display_type'] if annotations_info['annotations'][annotation['name']]['display_type'] else 'text'
        severity = annotations_info['annotations'][annotation['name']]['severity']

        # If updating an annotation, use the original_project_id to ensure the update occurs
        print('Updating: ', annotation['name'], sep = '')
        value_type = annotation['value_type']
        annotation_id = annotation['id']
        annotation_uid = annotation['uid']
        project.put_variant_annotation(annotation_id, name = annotation['name'], value_type = value_type, display_type = display_type, severity = severity, category = category)

# Input options
def parse_command_line():
  global version
  parser = argparse.ArgumentParser(description='Process the command line')

  # Required arguments
  parser.add_argument('--config', '-c', required = True, metavar = 'string', help = 'The config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The directory where the Python api wrapper lives')

  # The id of the project
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The id of the project whose private annotations are to be updated')

  # Define the json file with descriptions for the private attributes
  parser.add_argument('--json', '-j', required = True, metavar = 'string', help = 'The json file describing the annotation resources')

  # Version
  parser.add_argument('--version', '-v', action="version", version='Calypso annotation pipeline version: ' + str(version))

  return parser.parse_args()

# Read through the Mosaic json file describing the mosaic information for uploading annotations
def read_annotations_json(json_filename):
  allowed_references = ['GRCh37', 'GRCh38']
  json_info = {}

  # Try and open the file
  try:
    json_file = open(json_filename, 'r')
  except:
    fail('The file describing the annotations (' + str(json_filename) + ') could not be found')

  # Extract the json information
  try:
    json_data = json.loads(json_file.read())
  except:
    fail('The json file (' + str(json_filename) + ') is not valid')

  # Store the data version
  try:
    json_info['version'] = json_data['version']
  except:
    fail('The json file (' + str(json_filename) + ') does not include a version')

  # Store the reference
  try:
    json_info['reference'] = json_data['reference']
  except:
    fail('The json file (' + str(json_filename) + ') does not include a reference')
  if json_info['reference'] not in allowed_references:
    fail('The json file (' + str(json_filename) + ') has an unknown reference (' + str(json_info['reference']) + '). Allowed values are:\n  ' + '\n  '.join(allowed_references))

  # Loop over all the specified annotations and add these to the public attributes project
  try:
    annotations = json_data['annotations']
  except:
    fail('The json file (' + str(json_filename) + ') does not include annotations to add to the public attributes project')
  json_info['annotations'] = {}
  for annotation in annotations:
    json_info['annotations'][annotation] = {}

    # The annotation name must be defined
    try:
      json_info['annotations'][annotation]['name'] = annotations[annotation]['name']
    except:
      fail('The json file does not contain the "name" field for annotation "' + str(annotation) + '"')

    # The annotation type ('float' or 'string') is required
    try:
      json_info['annotations'][annotation]['type'] = annotations[annotation]['type']
    except:
      fail('The json file does not contain the "type" field for annotation "' + str(annotation) + '"')

    # Check if the annotation has a category, display_type and severity
    json_info['annotations'][annotation]['category'] = annotations[annotation]['category'] if 'category' in annotations[annotation] else False
    json_info['annotations'][annotation]['display_type'] = annotations[annotation]['display_type'] if 'display_type' in annotations[annotation] else False
    json_info['annotations'][annotation]['severity'] = annotations[annotation]['severity'] if 'severity' in annotations[annotation] else False

  # Return the annotation information
  return json_info

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

# Initialise global variables

# Pipeline version
version = "0.0.1"
date    = str(date.today())

# Store information related to Mosaic
mosaicConfig = {}

if __name__ == "__main__":
  main()
