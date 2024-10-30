import os
import argparse
import json
import sys
import time

from os.path import exists
from pprint import pprint
from sys import path

def main():

  # Parse the command line
  args = parse_command_line()

  # If the api_client path was not specified, get it from the script path
  try:
    args.api_client = os.path.dirname(os.path.realpath(__file__)).split('api_client')[0] + str('api_client')
  except:
    fail('Could not get the api_client path from the command. Please specify using --api_client / -a')

  # Import the api client
  path.append(args.api_client)
  from mosaic import Mosaic, Project, Store
  api_store = Store(config_file = args.config)
  api_mosaic = Mosaic(config_file = args.config)
  project = api_mosaic.get_project(args.project_id)

  # Check if this is a collection
  data = project.get_project()
  if data['is_collection']:
    project_ids = []
    for project_id in data['collection_project_ids']:
      project_ids.append(project_id)
  else:
    project_ids = [args.project_id]

  # Loop over all the projects
  for project_id in project_ids:
    project = api_mosaic.get_project(project_id)
    print('Updating filters for project: ', project.name, ' (', project_id, ')', sep = '')
    for variant_filter in project.get_variant_filters():
      filter_id = variant_filter['id']
      #project.delete_variant_filter(filter_id)

    # Get information on the sample available in the Mosaic project. Some variant filters require filtering on genotype. The variant filter
    # description will contain terms like "Proband": "alt". Therefore, the term Proband needs to be converted to a Mosaic sample id. If
    # genotype based filters are being omitted, this can be skipped
    samples = {}
    has_proband = False
    proband = False
    if not args.no_genotype_filters:
      samples = {}
      for sample in project.get_samples():
        samples[sample['name']] = {'id': sample['id'], 'relation': False}
        for attribute in project.get_attributes_for_sample(sample['id']):
          if attribute['uid'] == 'relation':
            for value in attribute['values']:
              if value['sample_id'] == sample['id']:
                samples[sample['name']]['relation'] = value['value']
                if value['value'] == 'Proband':
                  if has_proband: fail('Multiple samples in the Mosaic project are listed as the proband')
                  has_proband = True
                  proband = sample['name']
                break

    # Get all of the annotations in the current project. When creating a filter, the project will be checked to ensure that it has all of the
    # required annotations before creating the filter
    annotation_uids = {}
    for annotation in project.get_variant_annotations():

      # Loop over the annotation versions and get the latest (highest id)
      highest_annotation_version_id = False
      latest_annotation_version_id = False
      for annotation_version in annotation['annotation_versions']:
        if annotation_version['version'] == 'Latest':
          latest_annotation_version_id = annotation_version['id']
        if not highest_annotation_version_id:
          highest_annotation_version_id = annotation_version['id']
        elif annotation_version['id'] > highest_annotation_version_id:
          highest_annotation_version_id = annotation_version['id']
        if latest_annotation_version_id:
          annotation_version_id = latest_annotation_version_id
        else:
          annotation_version_id = highest_annotation_version_id

      annotation_uids[annotation['uid']] = {'id': annotation['id'], 'annotation_version_id': annotation_version_id, 'name': annotation['name'], 'type': annotation['value_type'], 'privacy_level': annotation['privacy_level']}

    # Create a dictionary of private annotation names with their uids
    private_annotation_names = {}
    for annotation_uid in annotation_uids:
      if annotation_uids[annotation_uid]['privacy_level'] == 'private':
        name = annotation_uids[annotation_uid]['name']
        if name in private_annotation_names:
          fail('ERROR: Multiple private annotations with the same name (' + str(name) + ' exist in the project, but there can only be one')
        else:
          private_annotation_names[name] = annotation_uid

    # Get HPO terms from Mosaic
    hpo_terms = []
    for hpo_term in project.get_sample_hpo_terms(samples[proband]['id']):
      hpo_terms.append({'hpo_id': hpo_term['hpo_id'], 'label': hpo_term['label']})

    # Determine all of the variant filters that are to be added; remove any filters that already exist with the same name; fill out variant
    # filter details not in the json (e.g. the uids of private annotations); create the filters; and finally update the project settings to
    # put the filters in the correct category and sort order. Note that the filters to be applied depend on the family structure. E.g. de novo
    # filters won't be added to projects without parents
    sample_map = create_sample_map(samples)
    filters = get_filters(project, filters_info, filter_categories, filters, samples, sample_map, annotation_uids, private_annotation_names, hpo_terms)

    # Create all the required filters and update their categories and sort order in the project settings
    create_filters(project, annotation_uids, filter_categories, filters)

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line')

  # Required arguments
  parser.add_argument('--config', '-c', required = True, metavar = 'string', help = 'The config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The directory where the Python api wrapper lives')

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print(message, sep = '')
  exit(1)

# Throw a warning
def warning(message):
  print('WARNING: ', message, sep = '')

# Initialise global variables

if __name__ == "__main__":
  main()
