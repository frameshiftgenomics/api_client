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

  try:
    project = api_mosaic.get_project(args.project_id)
  except Exception as e:
    fail('failed to open project. Error was: ' + str(e))

  # Check that the maternal or paternal samples exist in the project
  samples = []
  maternal_id = None
  paternal_id = None
  if args.maternal_id or args.paternal_id:

    if args.maternal_id == args.paternal_id:
      fail('maternal_id and paternal_id cannot be the same')
    for sample in project.get_samples():
      samples.append(int(sample['id']))
    if args.maternal_id:
      if int(args.maternal_id) not in samples:
        fail('unknown sample id for mother')
      else:
        maternal_id = args.maternal_id
    if args.paternal_id:
      if int(args.paternal_id) not in samples:
        fail('unknown sample id for father')
      else:
        paternal_id = args.paternal_id

  # Set the affaction status and sex
  affection_status = 2 if args.affection_status else 1
  sex = 0
  if args.sex:
    if args.sex == 'Male' or args.sex == 'male' or args.sex == 'm' or args.sex == 'M':
      sex = 1
    elif args.sex == 'Female' or args.sex == 'female' or args.sex == 'f' or args.sex == 'F':
      sex = 2
    else:
      fail('unknown biolgical sex')

  # Post the pedigree
  try:
    project.post_pedigree(args.sample_id, maternal_id = maternal_id, paternal_id = paternal_id, affection_status = affection_status, sex = sex, kindred_id = args.kindred_id)
  except Exception as e:
    fail('failed to post pedigree. Error was: ' + str(e))

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

  # The project and sample ids
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id')
  project_arguments.add_argument('--sample_id', '-s', required = True, metavar = 'integer', help = 'The Mosaic sample id')

  # Additional pedigree information
  optional_arguments.add_argument('--maternal_id', '-mi', required = False, metavar = 'integer', help = 'The sample id of the mother.')
  optional_arguments.add_argument('--paternal_id', '-pi', required = False, metavar = 'integer', help = 'The sample id of the father.')
  optional_arguments.add_argument('--affection_status', '-as', required = False, action = 'store_true', help = 'Set if the sample is affected')
  optional_arguments.add_argument('--sex', '-x', required = False, metavar = 'string', help = 'The biological sex of the sample. Male or Female')
  optional_arguments.add_argument('--kindred_id', '-k', required = False, metavar = 'string', help = 'The kindred id')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
