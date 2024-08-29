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
  args = parse_command_line()

  # Import the api client
  path.append(args.api_client)
  from mosaic import Mosaic, Project, Store
  api_store = Store(config_file = args.client_config)
  api_mosaic = Mosaic(config_file = args.client_config)

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # Get the project reference
  reference = project.get_project_settings()['reference']

  # Check if this is a collection
  data = project.get_project()
  if data['is_collection']:
    project_ids = data['collection_project_ids']
  else:
    project_ids = [args.project_id]

  # Loop over all the projects (for a collection) and apply the filters
  for project_id in project_ids:
    project = api_mosaic.get_project(project_id)
    print('Setting filters for project ', project.name, ' (id:', project_id,')', sep = '')

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
                  proband    = sample['name']
                break
  
    # Get all of the annotations in the current project. When creating a filter, the project will be checked to ensure that it has all of the
    # required annotations before creating the filter
    #annotations = {}
    #annotationUids = {}
    annotation_uids = {}
    for annotation in project.get_variant_annotations():
      #if annotation['name'] in annotations:
      #  print('WARNING: Multiple annotations with the name ' + str(annotation['name']) + ' exist. Only one annotation with the same name should exist in a project')
  
      # Loop over the annotation versions and get the latest (highest id)
      annotation_version_id = False
      for annotation_version in annotation['annotation_versions']:
        if not annotation_version_id:
          annotation_version_id = annotation_version['id']
        elif annotation_version['id'] > annotation_version_id:
          annotation_version_id = annotation_version['id']
  
      #annotations[annotation['name']] = {'id': annotation['id'], 'annotation_version_id': annotation_version_id, 'uid': annotation['uid'], 'type': annotation['value_type'], 'privacy_level': annotation['privacy_level']}
      annotation_uids[annotation['uid']] = {'id': annotation['id'], 'annotation_version_id': annotation_version_id, 'name': annotation['name'], 'type': annotation['value_type'], 'privacy_level': annotation['privacy_level']}
    #for annotation in annotations:
    #  annotationUids[annotations[annotation]['uid']] = {'name': annotation, 'type': annotations[annotation]['type'], 'annotation_version_id': annotations[annotation]['annotation_version_id']}

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
    #annotation_map = create_annotation_map(annotations, reference)
    filters_info = read_variant_filters_json(args.variant_filters)
    filter_categories, filters = get_filter_categories(filters_info)
    #filters = getFilters(filters_info, filter_categories, filters, samples, sample_map, annotations, annotationUids, annotation_map, annotationUids, hpo_terms)
    filters = get_filters(filters_info, filter_categories, filters, samples, sample_map, annotation_uids, private_annotation_names, hpo_terms)
  
    # Get all of the filters that exist in the project, and check which of these share a name with a filter to be created
    delete_filters(project, args.project_id, filters)
  
    # Create all the required filters and update their categories and sort order in the project settings
    create_filters(project, annotation_uids, filter_categories, filters)

# Input options
def parse_command_line():
  global version
  parser = argparse.ArgumentParser(description='Process the command line')

  # Required arguments
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = True, metavar = 'string', help = 'The api_client directory')
  parser.add_argument('--project_id', '-p', required = True, metavar = 'string', help = 'The project id that variants will be uploaded to')
  parser.add_argument('--variant_filters', '-f', required = True, metavar = 'string', help = 'The json file describing the variant filters to apply to each project')

  # Optional mosaic arguments
  parser.add_argument('--no_genotype_filters', '-n', required = False, action = "store_true", help = 'If set, all filters that include genotypes will be omitted')

  # Version
  parser.add_argument('--version', '-v', action="version", version='Calypso annotation pipeline version: ' + str(version))

  return parser.parse_args()

## Create a mapping from the sample relation to a Mosaic sample id. The json file describing the filter
## can include fields for requiring specific genotypes for family members, e.g. Proband must be an alt,
## in order to be general for any project. These need to be converted to sample ids for Mosaic
def create_sample_map(samples):
  sample_map = {}
  for sample in samples:
    if not samples[sample]['relation']:
      fail('Sample attribute "Relation" must be present and populated for all samples (no value exists for "' + str(sample) + '")')
    sample_map[samples[sample]['relation'].lower()] = samples[sample]['id']

  # Return the sample map
  return sample_map

# Create an annotation map that links general names for annotations to the specific annotation available
# in the project. For example, clinVar annotations can be regularly updated - when the filter is created,
# it needs to point to the clinVar annotation available in that project
def create_annotation_map(annotations, reference):
  annotation_map = {}
  #clinvar = []

  # Loop over all annotations in the project
  for annotation in annotations:

    # ClinVar can be regurlarly updated, so the filter can include the term 'clinvar_latest'. If this is
    # encountered, the filter should use the clinVar annotation available in the project
    #if 'clinvar' in annotation.lower():
    #  clinvar.append(annotation)

    # Private annotations will be referred to in the json by name, so these need to be included in the map
    if annotations[annotation]['privacy_level'] == 'private':
      annotation_map[annotation] = annotations[annotation]['uid']

  # If there is a single available clinVar annotation use this
  if len(clinvar) == 1:
    annotation_map['clinvar_latest'] = annotations[clinvar[0]]['uid']
  else:
    default_clinvar = 'ClinVar Significance ' + str(reference)
    uses_default = False
    for clinvar_option in clinvar:
      if clinvar_option == default_clinvar:
        annotation_map['clinvar_latest'] = annotations[clinvar[0]]['uid']
        uses_default = True
    if not uses_default:
      fail('Multiple ClinVar annotations exist in project. No logic exists to select the correct annotation')

  # Return the annotation map
  return annotation_map

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

# Extract all the variant filter categories from the json file
def get_filter_categories(filters_info):
  categories = {}
  filters = {}

  # The json should contain a "categories" section which includes the name of all the categories that filters
  # can be assigned to as well as the order of filters within the categories. Loop over the categories and validate all information
  if 'categories' not in filters_info:
     fail('The json file describing variant filters is missing the "categories" section')
  for category in filters_info['categories']:

    # For each category, loop over the names of the filters, and store their sort order. Check that there are no
    # duplicated sort positions
    categories[category] = {}
    for name in filters_info['categories'][category]:
      position = filters_info['categories'][category][name]
      if position in categories[category]:
        fail('Filter ' + str(name) + ' in category ' + str(category) + ' has the same sort position as a different filter')
      categories[category][position] = name
      if name in filters:
        fail('Filter "' + str(name) + '" appears multiple times in the filter description json')
      filters[name] = {'category': category, 'sortPosition': position}

  # Return the categories information
  return categories, filters

# Process all the information on the individual filters
def get_filters(filters_info, categories, filters, samples, sample_map, annotation_uids, private_annotation_names, hpo_terms):

  # Check all required sections and no others are present
  for section in filters_info:
    if section == 'categories':
      pass
    elif section == 'filters':
      pass
    else:
      fail('Unknown section (' + str(section) + ') in the variant filters json')
  if 'filters' not in filters_info:
    fail('The json file describing variant filters is missing the "filters" section')

  # Now check that all of the filters defined for each category are described in detail in the "filters" section of the json
  # Loop over all of the filters in the category and add them to the filterNames list. Check if any of the filters in
  # the categories section do not have a description in the 'filters' section
  filter_names = []
  for category in categories:
    for position in categories[category]:
      name = categories[category][position]
      if name not in filters_info['filters']:
        fail('Filter "' + str(name) + '" appears in filter category "' + str(category) + '", but is not described in the "filters" section')
      filter_names.append(categories[category][position])

  # If there are any filters that are uncategorized, throw an error
  for name in filters_info['filters']:
    if name not in filter_names:
      fail('Filter "' + str(name) + '" is not included in any category. Please include in a category')

  # Loop over the filters are process
  for category in categories:
    for position in categories[category]:
      name = categories[category][position]

      # Check if this filter has any requirements, for example, does it require that the case has parents (for e.g. de novo filters)    
      filters[name]['use_filter'] = check_requirements(filters_info['filters'][name], sample_map, hpo_terms)

      # If this filter is not to be applied to the project, the rest of the filter information can be ignored - e.g. if this is a
      # filter that requires the parents to be present, but they are not
      if filters[name]['use_filter']:
        filters[name]['info'] = filters_info['filters'][name]

        # Check the genotype information for the filter
        if 'genotypes' in filters[name]['info']:
          filters[name]['info'] = check_genotype_filters(filters[name]['info'], name, list(samples.keys()), sample_map)

        # Check all of the annotation filters
        filters[name]['info'] = check_annotation_filters(filters[name]['info'], name, annotation_uids, private_annotation_names)

        # Check for any HPO information
        if 'hpo_filters' in filters[name]['info']['filters']:
          filters[name]['info'] = check_hpo(filters[name]['info'], name, hpo_terms)

        # Now check if display is present. If so, this will describe how to update the variant table if this filter is applied. The only
        # allowable fields in this section are 'columns' which defines which column should show in the variant table, and 'sort' which
        # determines which annotation should be sorted on and how (ascending / descending). Set the "setDisplay" flag if this is required
        if 'display' in filters_info['filters'][name]:
          filters[name]['set_display'] = True
          for field in filters_info['filters'][name]['display']:

            # Process the "columns" field. This must contain a list of available annotation uids
            if field == 'column_uids':

              # Create a new list as some uids will need to be replaced in the list, but the order needs to be preserved
              ordered_uids = []
              filters[name]['column_uids'] = filters_info['filters'][name]['display'][field]
              for value in filters[name]['column_uids']: 
                if value in annotation_uids:
                  uid = value
                else:

                  # Instead of a uid, this could be the name of a private annotation
                  if value in private_annotation_names:
                    uid = private_annotation_names[value]
                  else:
                    fail('ERROR: Unknown value (' + str(uid) + ') in "display" > "column_uids" for variant filter ' + str(name))
                ordered_uids.append(uid)
              filters[name]['column_uids'] = ordered_uids

            # Process the "sort" field which defines the annotation to sort the table on
            elif field == 'sort':
              if 'column_uid' not in filters_info['filters'][name]['display']['sort']:
                fail('Field "column_uid" is missing from the "display" > "sort" section for filter ' + str(name))
              if 'direction' not in filters_info['filters'][name]['display']['sort']:
                fail('Field "direction" is missing from the "display" > "sort" section for filter ' + str(name))

              # Check the column to sort on is a valid uid, or is defined in the annotation map
              sort_uid = filters_info['filters'][name]['display'][field]['column_uid']
              if sort_uid in annotation_uids:
                uid = filters_info['filters'][name]['display'][field]['column_uid']
              else:

                # Instead of a uid, this could be the name of a private annotation
                if sort_uid in private_annotation_names:
                  uid = private_annotation_names[sort_uid]
                else:
                  fail('Unknown uid (' + str(sort_uid) + ') in "display" > "sort" > "column_uid" for variant filter ' + str(name))
              filters[name]['sort_column_uid'] = uid 

              # Check that the sort direction is valid
              filters[name]['sort_direction'] = filters_info['filters'][name]['display'][field]['direction']
              if filters[name]['sort_direction'] != 'ascending' and filters[name]['sort_direction'] != 'descending':
                fail('Sort direction must be "ascending" or "descending" for filter ' + str(name))

            else:
              fail('Unknown field in the "display" section for filter ' + str(name))
        else:
          filters[name]['set_display'] = False

  # Return the filter information
  return filters
























## Process all the information on the individual filters
#def getFilters(filtersInfo, categories, filters, samples, sampleMap, annotations, annotationUids, annotationMap, uids, hpoTerms):
#
#  # Check all required sections and no others are present
#  for section in filtersInfo:
#    if section == 'categories':
#      pass
#    elif section == 'filters':
#      pass
#    else:
#      fail('Unknown section (' + str(section) + ') in the variant filters json')
#  if 'filters' not in filtersInfo:
#    fail('The json file describing variant filters is missing the "filters" section')
#
#  # Now check that all of the filters defined for each category are described in detail in the "filters" section of the json
#  # Loop over all of the filters in the category and add them to the filterNames list. Check if any of the filters in
#  # the categories section do not have a description in the 'filters' section
#  filterNames = []
#  for category in categories:
#    for position in categories[category]:
#      name = categories[category][position]
#      if name not in filtersInfo['filters']:
#        fail('Filter "' + str(name) + '" appears in filter category "' + str(category) + '", but is not described in the "filters" section')
#      filterNames.append(categories[category][position])
#
#  # If there are any filters that are uncategorized, throw an error
#  for name in filtersInfo['filters']:
#    if name not in filterNames:
#      fail('Filter "' + str(name) + '" is not included in any category. Please include in a category')
#
#  # Loop over the filters are process
#  for category in categories:
#    for position in categories[category]:
#      name = categories[category][position]
#
#      # Check if this filter has any requirements, for example, does it require that the case has parents (for e.g. de novo filters)    
#      filters[name]['use_filter'] = checkRequirements(filtersInfo['filters'][name], sampleMap, hpoTerms)
#
#      # If this filter is not to be applied to the project, the rest of the filter information can be ignored - e.g. if this is a
#      # filter that requires the parents to be present, but they are not
#      if filters[name]['use_filter']:
#        filters[name]['info'] = filtersInfo['filters'][name]
#
#        # Check the genotype information for the filter
#        if 'genotypes' in filters[name]['info']:
#          filters[name]['info'] = checkGenotypeFilters(filters[name]['info'], name, list(samples.keys()), sampleMap)
#
#        # Check all of the annotation filters
#        filters[name]['info'] = checkAnnotationFilters(filters[name]['info'], name, annotations, annotationUids, annotationMap, uids)
#
#        # Check for any HPO information
#        if 'hpo_filters' in filters[name]['info']['filters']:
#          filters[name]['info'] = checkHpo(filters[name]['info'], name, hpoTerms)
#
#        # Now check if display is present. If so, this will describe how to update the variant table if this filter is applied. The only
#        # allowable fields in this section are 'columns' which defines which column should show in the variant table, and 'sort' which
#        # determines which annotation should be sorted on and how (ascending / descending). Set the "setDisplay" flag if this is required
#        if 'display' in filtersInfo['filters'][name]:
#          filters[name]['setDisplay'] = True
#          for field in filtersInfo['filters'][name]['display']:
#
#            # Process the "columns" field. This must contain a list of available annotation uids
#            if field == 'column_uids':
#
#              # Create a new list as some uids will need to be replaced in the list, but the order needs to be preserved
#              orderedUids = []
#              filters[name]['columnUids'] = filtersInfo['filters'][name]['display'][field]
#              for uid in filters[name]['columnUids']: 
#                if uid not in uids:
#                  if uid in annotationMap:
#                    orderedUids.append(annotationMap[uid])
#                  else:
#                    fail('Unknown uid (' + str(uid) + ') in "display" > "column_uids" for variant filter ' + str(name))
#                else:
#                  orderedUids.append(uid)
#              filters[name]['columnUids'] = orderedUids
#
#            # Process the "sort" field which defines the annotation to sort the table on
#            elif field == 'sort':
#              if 'column_uid' not in filtersInfo['filters'][name]['display']['sort']:
#                fail('Field "column_uid" is missing from the "display" > "sort" section for filter ' + str(name))
#              if 'direction' not in filtersInfo['filters'][name]['display']['sort']:
#                fail('Field "direction" is missing from the "display" > "sort" section for filter ' + str(name))
#
#              # Check the column to sort on is a valid uid, or is defined in the annotation map
#              sortUid = filtersInfo['filters'][name]['display'][field]['column_uid']
#              if sortUid not in uids:
#                if sortUid in annotationMap:
#                  uid = annotationMap[sortUid]
#                else:
#                  fail('Unknown uid (' + str(sortUid) + ') in "display" > "sort" > "column_uid" for variant filter ' + str(name))
#              else:
#                uid = filtersInfo['filters'][name]['display'][field]['column_uid']
#              filters[name]['sortColumnUid'] = uid 
#
#              # Check that the sort direction is valid
#              filters[name]['sortDirection'] = filtersInfo['filters'][name]['display'][field]['direction']
#              if filters[name]['sortDirection'] != 'ascending' and filters[name]['sortDirection'] != 'descending':
#                fail('Sort direction must be "ascending" or "descending" for filter ' + str(name))
#
#            else:
#              fail('Unknown field in the "display" section for filter ' + str(name))
#        else:
#          filters[name]['setDisplay'] = False
#
#  # Return the filter information
#  return filters

# Check if this filter has any requirements, for example, does it require that the case has parents (for e.g. de novo filters)    
def check_requirements(filters_info, sample_map, hpo_terms):
  use_filter = True

  # Check if parents are required for this filter. If so, check if they are present in the sample map. If not, this filter
  # should not be included in the project
  if 'requires_mother' in filters_info: 
    if filters_info['requires_mother'] and 'mother' not in sample_map:
      use_filter = False
  if 'requires_father' in filters_info: 
    if filters_info['requires_father'] and 'father' not in sample_map:
      use_filter = False

  # If this filter requires HPO terms and none are available, the filter should be skipped
  #if 'hpo_filters' in filters_info['filters'] and not hpo_terms:
  #  use_filter = False

  # Return whether this filter passes all requirements
  return use_filter

# Get information on the genotype filters and check they are valid
def check_genotype_filters(data, name, sample_ids, sample_map):

  # Store the allowed genotype options for saved filters
  genotype_options = []
  genotype_options.append('ref_samples')
  genotype_options.append('alt_samples')
  genotype_options.append('het_samples')
  genotype_options.append('hom_samples')

  # Check what genotype filters need to be applied and that the supplied genotypes are valid
  for genotype in data['genotypes']:
    if genotype not in genotype_options:
      fail('Mosaic variant filter with the name ' + str(name) + ', contains an unknown genotype option: ' + str(genotype))
    if not data['genotypes'][genotype]:
      continue

    # Check which samples need to have the requested genotype and add to the command. Use the supplied sampleIds
    # list to check that these samples are in the project
    sample_list = []
    if type(data['genotypes'][genotype]) != list:
      fail('Mosaic variant filter with the name ' + str(name) + ' has an invalid genotypes section')
    for sample in data['genotypes'][genotype]:

      # The genotype filter must either contain a valid sample id for the project, or the value in the json (e.g. proband)
      # must be present in the sampleMap and point to a valid sample id for this project
      sample_id = sample_map[sample] if sample in sample_map else False
      if not sample_id:
        try:
          sample_id = int(sample)
        except:
          fail('Mosaic variant filter ' + str(name) + ' references a sample with a non-integer id: ' + str(sample))
        if int(sample_id) not in sample_ids:
          fail('Mosaic variant filter ' + str(name) + ' references sample ' + str(sample) + ' which is not in the requested project')
      sample_list.append(sample_id)

    # Add the genotype filter to the filters listed in the json
    data['filters'][genotype] = sample_list

  # Return the updated data
  return data

## Process the annotation filters
#def checkAnnotationFilters(data, name, annotations, annotationUids, annotationMap, uids):
#
#  # Make sure the annotation_filters section exists
#  if 'annotation_filters' not in data['filters']:
#    fail('Annotation filter ' + str(name) + ' does not contain the required "annotation_filters" section')
#
#  # Check the filters provided in the json. The annotation filters need to extract the uids for the annotations, so
#  # ensure that each annotation has a valid uid (e.g. it is present in the project), and that supporting information
#  # e.g. a minimum value cannot be supplied for a string annotation, is valid
#  for aFilter in data['filters']['annotation_filters']:
#
#    # The json file must contain either a valid uid for a project annotation, the name of a valid private annotation, or
#    # have a name in the annotation map to relate a name to a uid. This is used for annotations (e.g. ClinVar) that are
#    # regularly updated, so the template does not need to be updated for updating annotations.
#    if 'uid' in aFilter:
#      uid = aFilter['uid']
#    elif 'name' in aFilter:
#
#      # Loop over the annotations in the annotation map and see if the requested annotation name is the beginning of any
#      # available annotations. For example, the filter could include an annotation name of "GQ Proband", but the project
#      # will have an annotation of the name "GQ Proband SAMPLE_NAME". As long as only a single annotation matches, this
#      # will be the annotation to use
#      matchedAnnotations = []
#      for annotation in annotationMap:
#        if aFilter['name'] in annotation:
#          matchedAnnotations.append(annotation)
#      if len(matchedAnnotations) == 1:
#        aFilter['uid'] = annotationMap[matchedAnnotations[0]]
#        del aFilter['name']
#
#      ## Check if this name is in the annotationMap and if so, use the mapped uid
#      #if aFilter['name'] in annotationMap:
#      #  aFilter['uid'] = annotationMap[aFilter['name']]
#      #  del aFilter['name']
#
#      # If the name is not in the annotationMap, check if a private annotation with this name exists in the project
#      else:
#        for annotation in annotations:
#          if str(annotation) == str(aFilter['name']):
#            aFilter['uid'] = annotations[annotation]['uid']
#            del aFilter['name']
#            break
#
#    # Store the uid and check that it exists
#    uid = aFilter['uid'] if 'uid' in aFilter else False
#    if not uid:
#      fail('Variant filter "' + str(name) + '" uses an unknown annotation: ' + str(aFilter['name']))
#    if uid not in uids:
#      fail('Variant filter "' + str(name) + '" uses an unknown annotation uid: ' + str(uid))
#
#    # Check that the filter defines whether or not to include null values
#    if 'include_nulls' not in aFilter:
#      fail('Annotation filter ' + str(name) + ' contains a filter with no "include_nulls" section')
#
#    # If the annotation is a string, the "values" field must be present
#    if uids[uid]['type'] == 'string':
#      if 'values' not in aFilter:
#        fail('Annotation filter ' + str(name) + ' contains a string based filter with no "values" section')
#      if type(aFilter['values']) != list:
#        fail('Annotation filter ' + str(name) + ' contains a string based filter with a "values" section that is not a list')
#
#    # If the annotation is a float, check that the specified operation is valid
#    elif uids[uid] == 'float':
#
#      # Loop over all the fields for the filter and check that they are valid
#      hasRequiredValue = False
#      for value in aFilter:
#        if value == 'uid':
#          continue
#        elif value == 'include_nulls':
#          continue
#
#        # The filter can define a minimum value
#        elif value == 'min':
#          try:
#            float(aFilter[value])
#          except:
#            fail('Annotation filter ' + str(name) + ' has a "min" that is not a float')
#          hasRequiredValue = True
#
#        # The filter can define a minimum value
#        elif value == 'max':
#          try:
#            float(aFilter[value])
#          except:
#            fail('Annotation filter ' + str(name) + ' has a "max" that is not a float')
#          hasRequiredValue = True
#
#        # Other fields are not recognised
#        else:
#          fail('Annotation filter ' + str(name) + ' contains an unrecognised field: ' + str(value))
#
#      # If no comparison fields were provided, fail
#      if not hasRequiredValue:
#        fail('Annotation filter ' + str(name) + ' contains a filter based on a float, but no comparison operators have been included')
#
#    # Include annotation_version_id for the selected uid
#    aFilter['annotation_version_id'] = annotationUids[aFilter['uid']]['annotation_version_id']
#
#  # Return the updated annotation information
#  return data

# Process the annotation filters
def check_annotation_filters(data, name, annotation_uids, private_annotation_names):

  # Make sure the annotation_filters section exists
  if 'annotation_filters' not in data['filters']:
    fail('Annotation filter ' + str(name) + ' does not contain the required "annotation_filters" section')

  # Check the filters provided in the json. The annotation filters need to extract the uids for the annotations, so
  # ensure that each annotation has a valid uid (e.g. it is present in the project), and that supporting information
  # e.g. a minimum value cannot be supplied for a string annotation, is valid
  for annotation_filter in data['filters']['annotation_filters']:

    # The json file must contain either a valid uid for a project annotation, the name of a valid private annotation, or
    # have a name in the annotation map to relate a name to a uid. This is used for annotations (e.g. ClinVar) that are
    # regularly updated, so the template does not need to be updated for updating annotations.
    if 'uid' in annotation_filter:
      uid = annotation_filter['uid']
    elif 'name' in annotation_filter:
      uid = False
      if annotation_filter['name'] in private_annotation_names:
        annotation_filter['uid'] = private_annotation_names[annotation_filter['name']]

      # If no private annotation with the correct name was found, fail
      else:
        fail('ERROR: no private annotation with the name ' + str(annotation_filter['name']) + ' found for filter ' + str(name))

      # Delete the name field from the filter once the uid, so the information is valid for the api
      del annotation_filter['name']

    # Store the uid and check that it exists
    uid = annotation_filter['uid'] if 'uid' in annotation_filter else False
    if not uid:
      fail('Variant filter "' + str(name) + '" uses an unknown annotation: ' + str(annotation_filter['name']))
    if uid not in annotation_uids:
      fail('Variant filter "' + str(name) + '" uses an unknown annotation uid: ' + str(uid))

    # Check that the filter defines whether or not to include null values
    if 'include_nulls' not in annotation_filter:
      fail('Annotation filter ' + str(name) + ' contains a filter with no "include_nulls" section')

    # If the annotation is a string, the "values" field must be present
    if annotation_uids[uid]['type'] == 'string':
      if 'values' not in annotation_filter:
        fail('Annotation filter ' + str(name) + ' contains a string based filter with no "values" section')
      if type(annotation_filter['values']) != list:
        fail('Annotation filter ' + str(name) + ' contains a string based filter with a "values" section that is not a list')

    # If the annotation is a float, check that the specified operation is valid
    elif annotation_uids[uid] == 'float':

      # Loop over all the fields for the filter and check that they are valid
      has_required_value = False
      for value in annotation_filter:
        if value == 'uid':
          continue
        elif value == 'include_nulls':
          continue

        # The filter can define a minimum value
        elif value == 'min':
          try:
            float(annotation_filter[value])
          except:
            fail('Annotation filter ' + str(name) + ' has a "min" that is not a float')
          has_required_value = True

        # The filter can define a minimum value
        elif value == 'max':
          try:
            float(annotation_filter[value])
          except:
            fail('Annotation filter ' + str(name) + ' has a "max" that is not a float')
          has_required_value = True

        # Other fields are not recognised
        else:
          fail('Annotation filter ' + str(name) + ' contains an unrecognised field: ' + str(value))

      # If no comparison fields were provided, fail
      if not has_required_value:
        fail('Annotation filter ' + str(name) + ' contains a filter based on a float, but no comparison operators have been included')

    # Include annotation_version_id for the selected uid
    annotation_filter['annotation_version_id'] = annotation_uids[annotation_filter['uid']]['annotation_version_id']

  # Return the updated annotation information
  return data

# Process the HPO filters. These are optional, so the script will not fail if they are not present
def check_hpo(data, name, hpo_terms):

  # Remove the HPO info from the data object. It will be returned in the format expected by Mosaic
  hpo_info = data['filters'].pop('hpo_filters')

  # If the "hpo_terms" field says proband, use the proband hpo terms
  if 'hpo_terms' not in hpo_info:
    fail('The hpo_filters for ' + str(name) + ' includes hpo_filters, but has no, "hpo_terms" field')
  if hpo_info['hpo_terms'] == 'proband':
    data['filters']['hpo_terms'] = hpo_terms
  else:
    fail('Unknown value for the hpo_filters > "hpo_terms" field for filter ' + str(name) + ': ' + str(hpo_info['hpo_terms']))

  # The number of overlaps is required. If this is set to a larger number than the number of available terms,
  # set the number of overlaps to the number of terms
  if 'hpo_min_overlap' not in hpo_info:
    fail('The hpo_filters for ' + str(name) + ' includes hpo_filters, but has no, "hpo_min_overlap" field')
  overlaps = hpo_info['hpo_min_overlap']
  if int(overlaps) > len(hpo_terms):
    overlaps = len(hpo_terms)
  data['filters']['hpo_min_overlap'] = overlaps

  # Return the updated data
  return data

# Get all of the filters that exist in the project, and check which of these share a name with a filter to be created
def delete_filters(project, project_id, filters):
  for existing_filter in project.get_variant_filters():
    if existing_filter['name'] in filters.keys():
      project.delete_variant_filter(existing_filter['id'])

# Create all the required filters and update their categories and sort order in the project settings
def create_filters(project, annotation_uids, categories, filters):
  sorted_filters = []
  for category in categories:
    record = {'category': category, 'sort_order': []}
    use_category = False
    for sort_id in sorted(categories[category]):
      name = categories[category][sort_id]

      # Create the filter, unless it has been marked as not to be added
      if filters[name]['use_filter']:

        # If the variant table display is getting modified, get the ids of the columns to show in the table as an array,
        # the id of the column to sort on and the sort direction
        column_ids = []
        sort_column_id = None
        sort_direction = None
        if filters[name]['set_display']:
          for column_uid in filters[name]['column_uids']:
            column_ids.append(annotation_uids[column_uid]['annotation_version_id'])
          sort_column_id = str(annotation_uids[filters[name]['sort_column_uid']]['annotation_version_id'])
          if filters[name]['sort_direction'] == 'ascending':
            sort_direction = 'ASC'
          elif filters[name]['sort_direction'] == 'descending':
            sort_direction = 'DESC'

        filter_info = project.post_variant_filter(name = name, category = category, column_ids = column_ids, sort_column_id = sort_column_id, sort_direction = sort_direction, filter_data = filters[name]['info']['filters'])
        filter_id = filter_info['id']
        record['sort_order'].append(str(filter_id))
        use_category = True

    # Populate the object used to update the Mosaic project settings. If no filters from this category passed the
    # requirements to be added, skip this step
    if use_category:
      sorted_filters.append(record)

  # Set the sort orders for all the categories
  if sorted_filters:
    text = ''
    for i, filters in enumerate(sorted_filters):
      if i == 0:
        text += '["VARIANT_FILTERS|' + str(filters['category']) + '", [' + ','.join(filters['sort_order']) + ']]'
      else:
        text += ', ["VARIANT_FILTERS|' + str(filters['category']) + '", [' + ','.join(filters['sort_order']) + ']]'
    sorted_annotations = {'sorted_annotations' : {}}
    sorted_annotations['sorted_annotations'] = {'variant_filters': text}
    project_settings = project.put_project_settings(sorted_annotations = sorted_annotations)

# If the script fails, provide an error message and exit
def fail(message):
  print(message, sep = "")
  exit(1)

# Initialise global variables

# Pipeline version
version = "1.1.6"

if __name__ == "__main__":
  main()
