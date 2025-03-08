import os
import argparse

from pprint import pprint
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
  api_store = Store(config_file = args.client_config)
  api_mosaic = Mosaic(config_file = args.client_config)

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # Get the vcf file name and full path
  vcf_file_name = args.vcf_file.split('/')[-1] if '/' in args.vcf_file else args.vcf_file
  tbi_file_name = vcf_file_name + '.tbi'
  vcf_path = os.path.abspath(args.vcf_file).rstrip(vcf_file_name)

  # Get the project reference
  reference = project.get_project_settings()['reference']

  # Get all the samples in the project as well as all files associated with them
  mosaic_samples = {}
  for sample in project.get_samples():
    mosaic_samples[sample['name']] = {'id': sample['id'], 'files': {}}
    for sample_file in project.get_sample_files(sample['id']):
      mosaic_samples[sample['name']]['files'][sample_file['name']] = sample_file['id']

  # Check that the input vcf file exists
  if not os.path.exists(args.vcf_file):
    fail('Could not find file ' + args.vcf_file)

  # Get all the samples from the vcf file
  if not args.tools_dir.endswith('/'):
    args.tools_dir = args.tools_dir + '/'
  bcftools = args.tools_dir + 'bcftools/bcftools'
  if not os.path.exists(bcftools):
    fail('Could not find bcftools executable')
  header = os.popen(bcftools + ' view -h ' + str(args.vcf_file)).read()
  for line in header.split('\n'):
    if line.startswith('#CHROM'):
      vcf_samples = line.rstrip().split('\t')[9:]
      break

  # Store the file ids to add to the experiment
  experiment_file_ids = []

  # Loop over the samples in the vcf file and find the ones in the mosaic_samples list
  for sample in vcf_samples:
    if sample not in mosaic_samples:
      fail('Sample ' + sample + ' in sv vcf file is not in Mosaic')
    sample_id = mosaic_samples[sample]['id']

    # Check if the vcf file is associated with the sample
    vcf_file_in_mosaic = False
    tbi_file_in_mosaic = False
    for sample_file in mosaic_samples[sample]['files']:
      if sample_file == vcf_file_name:
        vcf_file_id = mosaic_samples[sample]['files'][sample_file]
        vcf_file_in_mosaic = True
        experiment_file_ids.append(vcf_file_id)
      if sample_file == tbi_file_name:
        tbi_file_id = mosaic_samples[sample]['files'][sample_file]
        tbi_file_in_mosaic = True
        experiment_file_ids.append(tbi_file_id)

    # If the sample file is not attached to the sample in Mosaic, POST it
    if not vcf_file_in_mosaic:
      url = args.url_prepend + vcf_path + vcf_file_name if args.url_prepend else vcf_path + vcf_file_name
      vcf_file_id = project.post_sample_file(sample_id, name = vcf_file_name, nickname = vcf_file_name, reference = reference, file_type = 'vcf', uri = url, vcf_sample_name = sample)['id']
      experiment_file_ids.append(vcf_file_id)
    if not tbi_file_in_mosaic:
      url = args.url_prepend + vcf_path + tbi_file_name if args.url_prepend else vcf_path + tbi_file_name
      tbi_file_id = project.post_sample_file(sample_id, name = tbi_file_name, nickname = tbi_file_name, reference = reference, file_type = 'tbi', uri = url, vcf_sample_name = sample)['id']
      experiment_file_ids.append(tbi_file_id)

  # Set up the experiment information
  description = args.description if args.description else None
  experiment_type = args.experiment_type if args.experiment_type else None

  # Create the new experiment
  project.post_experiment(name = args.name, description = description, experiment_type = experiment_type, file_ids = experiment_file_ids)

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

  # The project id
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id')

  # The vcf file to create an experiment for
  parser.add_argument('--vcf_file', '-v', required = True, metavar = 'string', help = 'The vcf file to create an experiment for')

  # The vcf file to create an experiment for
  parser.add_argument('--tools_dir', '-t', required = True, metavar = 'string', help = 'The path to a tools directory (where to find bcftools')

  # If the file is being added to some file systems text needs to be prepended to the url
  parser.add_argument('--url_prepend', '-u', required = True, metavar = 'string', help = 'Text to prepend to the url - e.g. file://')

  # Information about the experiment
  parser.add_argument('--name', '-n', required = True, metavar = 'string', help = 'The name of the experiment to create')
  parser.add_argument('--description', '-d', required = False, metavar = 'string', help = 'A description of the experiment')
  parser.add_argument('--experiment_type', '-e', required = False, metavar = 'string', help = 'A type for the experiment, e.g. SV, RNA')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
