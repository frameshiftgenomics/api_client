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
  try:
    project = api_mosaic.get_project(args.project_id)
  except Exception as e:
    fail('Failed to open project. Error was: ' + str(e))

  # Get the variant sets in the project
  try:
    for variant_set in project.get_variant_sets():

      # If only Primary ClinVar sets are required, check that ClinVar and Primary appear in the set name
      if args.clinvar_primary:
        display = False
        name = variant_set['name']
        if 'ClinVar' in name and 'Primary' in name:
          display = True
          if args.clinvar_start_date:
            if clinvar_date_format(args.clinvar_start_date, 'start') not in name:
              display = False
          if args.clinvar_end_date:
            if clinvar_date_format(args.clinvar_end_date, 'end') not in name:
              display = False
          if display:
            print(variant_set['id'])

      # If all variants sets are to be output
      else:
        pprint(variant_set)
  except Exception as e:
    fail('Failed to get variants sets. Error was: ' + str(e))

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')
  api_arguments = parser.add_argument_group('API Arguments')
  project_arguments = parser.add_argument_group('Project Arguments')
  required_arguments = parser.add_argument_group('Required Arguments')
  optional_arguments = parser.add_argument_group('Optional Arguments')
  display_arguments = parser.add_argument_group('Display Information')
  clinvar_arguments = parser.add_argument_group('ClinVar Review Sets')

  # Define the location of the api_client and the ini config file
  api_arguments.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  api_arguments.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to get variants sets for')

  # Arguments for output ClinVar review variants
  clinvar_arguments.add_argument('--clinvar_primary', '-cp', required = False, action = 'store_true', help = 'If set, only return Primary ClinVar review variant sets')
  clinvar_arguments.add_argument('--clinvar_start_date', '-cs', required = False, metavar = 'string', help = 'If set, only return Primary ClinVar review variant sets with this start date (format: YYYYMMDD)')
  clinvar_arguments.add_argument('--clinvar_end_date', '-ce', required = False, metavar = 'string', help = 'If set, only return Primary ClinVar review variant sets with this end date (format: YYYYMMDD)')

  return parser.parse_args()

# Get the ClinVar date in the correct format
def clinvar_date_format(clinvar_date, text):
  if len(clinvar_date) != 8:
    fail('ClinVar ' + str(text) + ' date is not in the format YYYYMMDD')
  year = clinvar_date[0:4]
  month = clinvar_date[4:6]
  day = clinvar_date[6:8]

  # Return the formatted date
  return str(year) + '-' + str(month) + '-' + str(day)

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
