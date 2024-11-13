import os
import argparse

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

  # Check the name of the project
  if project.name != 'Mosaic GRCh37 Globals' and project.name != 'Mosaic GRCh38 Globals':
    fail('ClinVar version must be added to a Mosaic Globals project, not "' + project.name + '"')

  # Check that the ClinVar version version is a string of 8 integers
  if len(args.clinvar_version_a) != 8:
    fail('The original ClinVar version must be a string of 8 integers in the format YYYYMMDD')
  if len(args.clinvar_version_b) != 8:
    fail('The new ClinVar version must be a string of 8 integers in the format YYYYMMDD')
    
  # Get the reference of the project
  reference = project.get_project_settings()['reference']

  # Find the ClinVar annotation
  clinvar_annotation_name = 'ClinVar Significance ' + str(reference)
  annotation_id = None
  for annotation in project.get_variant_annotations():
    if annotation['name'] == clinvar_annotation_name:
      annotation_id = annotation['id']

  # Fail if the ClinVar annotation couldn't be found
  if not annotation_id:
    fail('Could not find an annotation called ' + clinvar_annotation_name)

  # Get the available annotation versions
  annotation_versions = {}
  for annotation_version in project.get_variant_annotation_versions(annotation_id):
    annotation_versions[annotation_version['version']] = annotation_version['id']

  # Check that the requested versions exist
  if args.clinvar_version_a not in annotation_versions:
    fail('The original ClinVar version (' + str(args.clinvar_version_a) + ') does not exist')
  if args.clinvar_version_b not in annotation_versions:
    fail('The new ClinVar version (' + str(args.clinvar_version_b) + ') does not exist')
  version_a_id = annotation_versions[args.clinvar_version_a]
  version_b_id = annotation_versions[args.clinvar_version_b]

  # Get the project ids to of the projects to check
  if args.project_ids_to_check:
    if ',' in args.project_ids_to_check:
      project_ids = args.project_ids_to_check.split(',')
    else:
      project_ids = [args.project_ids_to_check]

  # Generate a list of email addresses to send notifications to
  emails = None
  args.emails = args.emails.rstrip('"') if args.emails.endswith('"') else args.emails
  args.emails = args.emails.lstrip('"') if args.emails.startswith('"') else args.emails
  if args.emails:
    emails = args.emails.split(',') if ',' in args.emails else [args.emails]

  # Perform the diff
  generate_tasks = False if args.disable_tasks else True
  project.post_diff_clinvar_version(version_a = args.clinvar_version_a, version_b = args.clinvar_version_b, project_ids = project_ids, generate_tasks = generate_tasks, emails = emails)

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = True, metavar = 'string', help = 'The api_client directory')

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # The ClinVar versions to diff
  parser.add_argument('--clinvar_version_a', '-v', required = True, metavar = 'string', help = 'The original ClinVar version in the format YYYYMMDD')
  parser.add_argument('--clinvar_version_b', '-b', required = True, metavar = 'string', help = 'The new ClinVar version in the format YYYYMMDD')

  # A list of project ids can be supplied as a comma separated list
  parser.add_argument('--project_ids_to_check', '-i', required = True, metavar = 'string', help = 'A comma separated list of project ids to check for updated ClinVar variants')

  # A list of email address to notify about the update
  parser.add_argument('--emails', '-e', required = False, metavar = 'string', help = 'A comma separated list of email address to send notifications to')

  # Do not create any tasks in Mosaic. By default, create tasks
  parser.add_argument('--disable_tasks', '-d', required = False, action = 'store_true', help = 'By default, tasks will be created for all ClinVar variants to review. This flag will disable task creation')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  message = 'ERROR: ' + message
  print(message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
