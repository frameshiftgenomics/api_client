import os
import argparse

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

  # Loop over all samples in the project
  for sample in project.get_samples():
    for sample_file in project.get_sample_files(sample['id']):

      # If the file does not have a type, throw a warning
      if not sample_file['type']:
        print('WARNING: file ', sample_file['id'], ' (', sample_file['name'], ') has no type', sep = '')

      # If the file is a vcf or tbi file, check that the vcf_sample_name is set
      if sample_file['type'] == 'vcf' or sample_file['type'] == 'tbi':
        if not sample_file['vcf_sample_name']:
          print('WARNING: file ', sample_file['id'], ' (', sample_file['name'], ') does not have vcf_sample_name set', sep = '')
        elif sample_file['vcf_sample_name'] != sample['name']:
          print('WARNING: file ', sample_file['id'], ' (', sample_file['name'], ') has a different vcf_sample_name (', sample_file['vcf_sample_name'], ') to the sample name (', sample['name'], ')', sep = '')

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = True, metavar = 'string', help = 'The api_client directory')

  # The project id
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print(message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
