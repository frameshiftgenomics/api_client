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
  args = parseCommandLine()

  # Import the api client
  path.append(args.api_client)
  from mosaic import Mosaic, Project, Store
  api_store = Store(config_file = args.config)
  api_mosaic = Mosaic(config_file = args.config)
  project = api_mosaic.get_project(args.project_id)

  # Check that the json containing the required defaults exists and read in the information
  #if not exists(args.json): fail('Json file (' + str(args.json) + ') does not exist')
  try:
    json_file = open(args.json, 'r')
  except:
    fail('Could not open the json file: ' + str(args.json))
  try:
    json_info = json.load(json_file)
  except:
    fail('Could not read contents of json file ' + str(args.json) + '. Check that this is a valid json')
  json_file.close()

  # Check if this is a collection
  data = project.get_project()
  if data['is_collection']:
    project_ids = []
    for project_id in data['collection_project_ids']:
      project_ids.append(project_id)
  else:
    project_ids = [args.project_id]

  # Loop over all the projects (for a collection) and apply the filters
  for project_id in project_ids:
    project = api_mosaic.get_project(project_id)
    print('Setting project defaults for ', project.name, ' (id:', project_id,')', sep = '')

    # Get all the sample attributes in the project
    sample_attribute_names = {}
    sample_attribute_uids = {}
    sample_attribute_ids = []
    for sample_attribute in project.get_sample_attributes():

      # Check for duplicate sample attributes
      if sample_attribute['name'] in sample_attribute_names:
        fail('ERROR: there are multiple sample attributes with the name ' + str(sample_attribute['name']) + ' in project with id ' + str(project_id))
      sample_attribute_names[sample_attribute['name']] = sample_attribute['id']
      sample_attribute_uids[sample_attribute['uid']] = sample_attribute['id']
      sample_attribute_ids.append(sample_attribute['id'])

    # Get all the annotations in the project
    annotation_uids = {}
    annotation_names = {}
    for annotation in project.get_variant_annotations():
      annotation_uids[annotation['uid']] = annotation['id']
      annotation_names[annotation['name']] = annotation['id']
  
    #######
    #######
    # Set the samples table defaults
    #######
    #######
    samples_table_columns = []
    if 'sample_table' in json_info:
      for attribute_specifier in json_info['sample_table']:
        attribute_type = json_info['sample_table'][attribute_specifier]

        # If the attribute name was specified
        if attribute_type == 'name':
          if attribute_specifier not in sample_attribute_names:
            fail('ERROR: sample table defaults includes a sample attribute specified by name that is not available: ' + attribute_specifier)
          samples_table_columns.append(sample_attribute_names[attribute_specifier])

        # If the attribute uid was specified
        elif attribute_type == 'uid':
          if attribute_specifier not in sample_attribute_uids:
            fail('ERROR: sample table defaults includes a sample attribute specified by uid that is not available: ' + attribute_specifier)
          samples_table_columns.append(sample_attribute_uids[attribute_specifier])

        # If the attribute id was specified
        elif attribute_type == 'id':
          if attribute_specifier not in sample_attribute_ids:
            fail('ERROR: sample table defaults includes a sample attribute specified by id that is not available: ' + attribute_specifier)
          samples_table_columns.append(attribute_specifier)

    #######
    #######
    # Remove any specified annotations
    #######
    #######
    annotations_to_remove = []
    if 'remove_annotations' in json_info:
      for name in json_info['remove_annotations']:
        if name in annotations:
          data = project.delete_variant_annotation(annotations[name])

    # Set the variants table defaults. The json file can include annotation names, ids or version ids, but they must be
    # specified. If an annotation name, uid, or id is supplied, the "latest" annotation version id will be used, or, if this
    # doesn't exist, the "default" will be used
    if 'annotations'in json_info:
      annotation_version_ids = get_variant_table_ids(project, project_id, json_info['annotations'], annotation_names, annotation_uids)
    if 'watchlist_annotations'in json_info:
      watchlist_version_ids = get_variant_table_ids(project, project_id, json_info['watchlist_annotations'], annotation_names, annotation_uids)

    # Get the id of the variant watchlist if it is listed as to be pinned
    if 'pin_watchlist' in json_info:
      if json_info['pin_watchlist']:
        print('Pinning watchlist to the dashboard')
        watchlist_id = False
        for variant_set in project.get_variant_sets():
          if variant_set['name'] == 'Variant Watchlist':
            watchlist_id = variant_set['id']
            break
        if watchlist_id:
          project.post_project_dashboard(dashboard_type = 'variant_set', is_active = 'true', variant_set_id = watchlist_id)

    # Set the project settings
    data = project.put_project_settings(selected_sample_attribute_column_ids = samples_table_columns, \
           selected_variant_annotation_version_ids = annotation_version_ids, \
           default_variant_set_annotation_ids = watchlist_version_ids)
  
# Input options
def parseCommandLine():
  global version
  parser = argparse.ArgumentParser(description='Process the command line')

  # Required arguments
  parser.add_argument('--config', '-c', required = True, metavar = 'string', help = 'The config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = True, metavar = 'string', help = 'The directory where the Python api wrapper lives')

  # Optional pipeline arguments
  parser.add_argument('--json', '-j', required = True, metavar = 'string', help = 'The json file describing the project defaults')

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # Version
  parser.add_argument('--version', '-v', action="version", version='Calypso annotation pipeline version: ' + str(version))

  return parser.parse_args()

# Get the annotation version ids
def get_variant_table_ids(project, project_id, data, annotation_names, annotation_uids):
  annotation_version_ids = []
  annotations_to_import = False
  for annotation in data:
    annotation_uid = data[annotation]['uid']
    annotation_version = data[annotation]['version']

    # There may be private annotations that should be included in the defaults. These will have a uid of False
    if not annotation_uid:
      if annotation not in annotation_names:
        fail('ERROR: annotation "' + str(annotation) + '" has no uid provided (assumed to be a private annotation), but no annotation of this name exists in project ' + str(project_id))
      annotation_id = annotation_names[annotation]

    # If the uid does not correspond to an annotation in the project it will need to be imported
    elif annotation_uid not in annotation_uids:

      # If annotations_to_import doesn't exist, get all the annotations that can be imported.
      # We only call this route if it's required, but once it exists, get the id of the annotation
      # that has been specified and import it
      if not annotations_to_import:
        annotations_to_import = {}
        for import_annotation in project.get_variant_annotations_to_import():
          annotations_to_import[import_annotation['uid']] = import_annotation['id']

      # Get the id of the annotation to import and import it
      annotation_id = annotations_to_import[uid]
      project.post_import_annotation(annotation_id)

    # Otherwise, just get the annotation id for the annotation in the project
    else:
      annotation_id = annotation_uids[annotation_uid]

    # Get the annotation versions
    annotation_versions = {}
    for version_info in project.get_variant_annotation_versions(annotation_id):
      annotation_versions[version_info['version']] = version_info['id']

    # Find the id for the required version, if the default version was specified...
    if annotation_version == 'default':
      if 'default' not in annotation_versions:
        fail('ERROR: annotation "' + str(annotation) + '" is set to use the "default" version, but this does not exist for this annotation')
      annotation_version_ids.append(annotation_versions['default'])

    # ... if the latest version was specified...
    elif annotation_version == 'latest':
      if 'latest' not in annotation_versions:
        fail('ERROR: annotation "' + str(annotation) + '" is set to use the "latest" version, but this does not exist for this annotation')
      annotation_version_ids.append(annotation_versions['latest'])

    # ... or if the version id was specified
    else:
      has_version_id = False
      for version_info in annotation_versions:
        if annotation_version == annotation_versions[version_info]:
          annotation_version_ids.append(annotation_version)
          has_version_id = True
          break
      if not has_version_id:
        fail('ERROR: annotation "' + str(annotation) + '" lists "' + str(annotation_version) + '" as the annotation version. This must be "default", "latest", or a valid annotation_version_id')

  # Return the list of version ids
  return annotation_version_ids

# If the script fails, provide an error message and exit
def fail(message):
  print(message, sep = '')
  exit(1)

# Throw a warning
def warning(message):
  print('WARNING: ', message, sep = '')

# Initialise global variables

# Pipeline version
version = "0.0.1"

if __name__ == "__main__":
  main()
