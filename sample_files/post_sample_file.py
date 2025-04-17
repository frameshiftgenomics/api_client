import os
import argparse

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

  # Delete the file
  project.post_sample_file(args.sample_id, url=args.endpoint_url, experiment_id=args.experiment_id, library_type=args.library_type, name=args.name, nickname=args.nickname, qc=args.qc, reference=args.reference, file_type=args.file_type, size=args.size, uri=args.uri, vcf_sample_name=args.vcf_sample_name)

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

  # The project and sample ids to which the file is to be added are required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')
  parser.add_argument('--sample_id', '-s', required = True, metavar = 'integer', help = 'The sample id of the sample the file is to be attached to')

  # Required arguments related to the file to add
  parser.add_argument('--name', '-n', required = True, metavar = 'string', help = 'The name of the file to add')
  parser.add_argument('--reference', '-r', required = True, metavar = 'string', help = 'The reference genome of the project')
  parser.add_argument('--file_type', '-t', required = True, metavar = 'string', help = 'The file type of the file being added (e.g. vcf)')
  parser.add_argument('--uri', '-u', required = True, metavar = 'string', help = 'The location of the file being added')

  # Optional arguments related to the file to add
  parser.add_argument('--nickname', '-k', required = False, metavar = 'string', help = 'The nickname of the file to add')
  parser.add_argument('--endpoint_url', '-d', required = False, metavar = 'string', help = 'The id of the experiment this file should be added to')
  parser.add_argument('--experiment_id', '-e', required = False, metavar = 'integer', help = 'The id of the experiment this file should be added to')
  parser.add_argument('--library_type', '-l', required = False, metavar = 'string', help = 'The library type of the sequencing data')
  parser.add_argument('--qc', '-q', required = False, metavar = 'json', help = 'Json file containing qc information for the file')
  parser.add_argument('--size', '-z', required = False, metavar = 'integer', help = 'The size in bytes of the file')
  parser.add_argument('--vcf_sample_name', '-v', required = False, metavar = 'string', help = 'The sample identifier in the vcf file')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
