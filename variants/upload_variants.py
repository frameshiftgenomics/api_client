import os
import argparse
from pprint import pprint

from sys import path

def main():

  # Parse the command line
  args = parse_command_line()

  # If the api_client path was not specified, get it from the script path
  if args.api_client:
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
  has_vcfs = False
  for sample in project.get_samples():
    for sample_file in project.get_sample_files(sample['id']):
      if sample_file['type'] == 'vcf':
        has_vcfs = True
        break
  if not has_vcfs and not args.sample_map:
    fail('project has no associated vcf files and so a sample map (--sample_map, -s) is required')

  sample_map = args.sample_map if args.sample_map else None

  # Upload the variants
  notifications = 'false' if args.enable_notifications else 'true'
  data = project.post_variant_file(args.vcf, upload_type = args.method, disable_successful_notification = notifications, sample_map=sample_map)
  print(data['message'], '. Variant upload job id: ', data['redis_job_id'], sep = '')

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to add variant filters to')

  # Additional arguments
  parser.add_argument('--method', '-m', required = True, metavar = 'string', help = 'The variant upload method: "allele, no-validation, position, raw, sv-no-validation"')
  parser.add_argument('--vcf', '-v', required = True, metavar = 'string', help = 'The vcf file to upload variants from')
  parser.add_argument('--enable_notifications', '-e', required = False, action = 'store_true', help = 'If set, notifications will be provided. Otherwise, notifications will only be provided for failures')

  # If there is no vcf file attached to the project, we need a file connecting the sample ids to the vcf sample names
  parser.add_argument('--sample_map', '-s', required = False, metavar = 'string', help = 'The sample map file which is required if there are no vcf files attached to the project')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
