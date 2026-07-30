import os
import json
import sys
import time

from os.path import exists
from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, warning, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)
  project = api_mosaic.get_project(args.project_id)

  # Check if this is a collection
  data = project.get_project()
  if data['is_collection']:
    project_ids = []
    for project_id in data['collection_project_ids']:
      project_ids.append(project_id)
  else:
    project_ids = [args.project_id]

  # Define the bcftools command
  bcftools = '/scratch/ucgd/lustre-labs/marth/scratch/calypso/tools/bcftools/bcftools'

  # Define the ClinVar version and vcf file
  clinvar_version = 'clinvar_significance_grch38@' + str(args.clinvar_version)
  file_path = str(args.clinvar_file_path) + '/' if not args.clinvar_file_path.endswith('/') else args.clinvar_file_path
  clinvar_file = str(args.clinvar_file_path) + 'clinvar_' + str(args.clinvar_version) + '.vcf.gz'

  # Loop over all tasks associated with these projects
  for task in api_mosaic.get_tasks(categories = None, completed = None, project_ids = project_ids, types = None, order_dir = None):
    project = api_mosaic.get_project(task['project_id'])
    for variant_id in project.get_variant_set(task['variant_set_id'])['variant_ids']:
      variant_data = project.get_variant(variant_id, include_annotation_data = 'true')
      for annotation in variant_data:
        if clinvar_version in annotation:
          if 'Conflicting_classifications_of_pathogenicity' in variant_data[annotation]:
            position = str(variant_data['chr']) + ':' + str(variant_data['r_start'])
            command = str(bcftools) + ' view -H -i \'REF == "' + str(variant_data['ref']) + '" && ALT == "' + str(variant_data['alt']) + '"\' ' + str(clinvar_file) + ' ' + str(position)
            for field in os.popen(command).read().split('\t')[7].split(';'):
              has_path = False
              url = 'https://udn.mosaic.frameshift.io/#/projects/' + str(task['project_id']) + '/variants?variant_set_id=' + str(task['variant_set_id'])
              if field.startswith('CLNSIGCONF='):
                for assertion in field.split('=')[1].split('|'):
                  if 'athogenic' in assertion:
                    has_path = True
                    break
                if not has_path:
                  print(task['project_name'], field, url, sep = ',')
                break

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # The ClinVar version to output
  parser.add_argument('--clinvar_version', '-v', required = True, metavar = 'integer', help = 'The ClinVar version to check')

  # The path to the ClinVar vcf file
  parser.add_argument('--clinvar_file_path', '-f', required = True, metavar = 'string', help = 'The path to the ClinVar vcf file')

  return parser.parse_args()

# Throw a warning
def warning(message):
  print('WARNING: ', message, sep = '')

# Initialise global variables

if __name__ == "__main__":
  main()
