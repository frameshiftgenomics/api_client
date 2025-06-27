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

  # Make sure conflicting display options aren't selected
  if sum([args.ids_only, args.file_names_only, args.display_all_information]) > 1:
    fail('Conflicting display options selected')

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # Check the input arguments
  combine_duplicates = 'true' if args.combine_duplicates else 'false'
  file_types = []
  if args.file_types:
    file_types = args.file_types.split(',') if ',' in args.file_types else [args.file_types]
  sample_names = []
  if args.sample_names:
    sample_names = args.sample_names.split(',') if ',' in args.sample_names else [args.sample_names]

  # Get all of the sample files
  for sample_file in project.get_all_sample_files(combine_duplicates = combine_duplicates, file_types = file_types, sample_names = sample_names):

    # If combine duplicates is set, arrays will be returned
    if args.combine_duplicates:
      if args.ids_only:
        print(sample_file['file_ids'], sep = '')
      elif args.file_names_only:
        for sample_file_name in sample_file['file_names']:
          print(sample_file_name)
      elif args.uris_only:
        print(sample_file['uri'])
      else:
        if not args.display_all_information:
          print(sample_file['sample_names'], ': ', sample_file['file_ids'], ', ', sample_file['type'], sep = '')
        else:
          print(sample_file['file_names'])
          print('  id: ', sample_file['file_ids'], sep = '')
          print('  type: ', sample_file['type'], sep = '')
          print('  uri: ', sample_file['uri'], sep = '')
          print('  vcf sample names:')
          for vcf_sample_name in sample_file['vcf_sample_names']:
            print('    ', vcf_sample_name['vcf_sample_name'], ': ', vcf_sample_name['sample_id'], sep = '')
    else:
      if args.ids_only:
        print(sample_file['id'])
      elif args.file_names_only:
        print(sample_file['name'])
      else:
        if not args.display_all_information:
          print(sample_file['name'], ': ', sample_file['id'], ', ', sample_file['type'], sep = '')
        else:
          print(sample_file['name'])
          print('  id: ', sample_file['id'], sep = '')
          print('  type: ', sample_file['type'], sep = '')
          print('  uri: ', sample_file['uri'], sep = '')
          print('  vcf sample name: ', sample_file['vcf_sample_name'], sep = '')

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')
  api_arguments = parser.add_argument_group('API Arguments')
  project_arguments = parser.add_argument_group('Project Arguments')
  required_arguments = parser.add_argument_group('Required Arguments')
  optional_arguments = parser.add_argument_group('Optional Arguments')
  display_arguments = parser.add_argument_group('Display Information')

  # Define the location of the api_client and the ini config file
  api_arguments.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  api_arguments.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # Determine what information to print to screen
  optional_arguments.add_argument('--file_types', '-t', required = False, metavar = 'string', help = 'A comma separated list of file types to return')
  optional_arguments.add_argument('--sample_names', '-n', required = False, metavar = 'string', help = 'A comma separated list of sample names to return files for')
  optional_arguments.add_argument('--combine_duplicates', '-d', required = False, action = 'store_true', help = 'If set, files with the same url will be combined')

  # Determine what information to print to screen
  display_arguments.add_argument('--ids_only', '-io', required = False, action = 'store_true', help = 'Only return project ids')
  display_arguments.add_argument('--file_names_only', '-fo', required = False, action = 'store_true', help = 'Only return file names')
  display_arguments.add_argument('--uris_only', '-uo', required = False, action = 'store_true', help = 'Only return urls')
  display_arguments.add_argument('--display_all_information', '-da', required = False, action = 'store_true', help = 'Display all information about the attributes')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
