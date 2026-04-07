import os
import argparse

from sys import path
from pprint import pprint

def main():
  global api_mosaic
  global allowed_references
  global system_projects

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

  # Check that the requested activity type is valid
  ### REPLACE WHEN ENDPOINT IS AVAILABLE TO GET VALUES
  allowed_activity_types = {'comment_posted': 1,
                            'conversation_posted': 2,
                            'sample_added': 3,
                            'attribute_added': 4,
                            'variants_added': 5,
                            'user_added': 6,
                            'expression_data_added': 7,
                            'variant_annotation_added': 8,
                            'gene_annotation_added': 9,
                            'analysis_published': 10,
                            'variant_set_published': 11,
                            'gene_set_published': 12,
                            'project_attribute_updated': 13,
                            'project_attribute_added': 14,
                            'collection_projects_added': 15,
                            'collection_projects_removed': 16,
                            'sample_set_published': 17,
                            'user_removed': 18,
                            'file_downloaded': 19,
                            'project_created': 20,
                            'project_deleted': 21,
                            'experiment_added': 22,
                            'job_submitted': 23,
                            'task_completed': 34,
                            'project_archived': 41,
                            'project_unarchive_requested': 42}
  if args.activity_type:
    if args.activity_type not in allowed_activity_types:
      fail('unknown activity type. Must be one of the following: ' + ', '.join(allowed_activity_types))

  # Open a project
  try:
    project = api_mosaic.get_project(args.project_id)
  except Exception as e:
    fail('failed to open project. Error was: ' + str(e))

  # Get the activities
  try:
    for activity in project.get_activities(from_date = args.from_date, to_date = args.to_date):
      is_display = True
      if args.activity_type:
        if args.activity_type != activity['type']:
          is_display = False

      # Display the requested activities
      if is_display:
        if args.display_raw_information:
          pprint(activity)
        elif args.output_ids_only:
          print(activity['id'])

        # Default output
        else:
          print(activity['id'], ': ', activity['type'], sep = '')
  except Exception as e:
    fail('failed to get activities. Error was: ' + str(e))

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

  # Limit search to specific projects
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id')

  # Additional filters
  optional_arguments.add_argument('--activity_type', '-t', required = False, metavar = 'string', help = 'Only display avtivities of this type')
  optional_arguments.add_argument('--from_date', '-fd', required = False, metavar = 'string', help = 'Only output activities after this date')
  optional_arguments.add_argument('--to_date', '-td', required = False, metavar = 'string', help = 'Only output activities before this date')

  # Display arguments
  optional_arguments.add_argument('--output_ids_only', '-io', required = False, action = 'store_true', help = 'Only output the activity ids')
  optional_arguments.add_argument('--display_raw_information', '-dr', required = False, action = 'store_true', help = 'Show the full, raw activity information')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

api_mosaic = None

if __name__ == "__main__":
  main()
