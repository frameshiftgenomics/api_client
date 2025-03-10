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

  # Determine which tasks to return based on categories
  categories = None
  if args.categories:
    category_list = args.categories.split(',') if ',' in args.categories else [args.categories]
    for category in category_list:
      if category == 'project_setup':
        categories.append(category)
      elif category == 'review_variants':
        categories.append(category)
      elif category == 'all':
        categories.append('project_setup')
        categories.append('review_variants')
      else:
        fail('--categories / -g must take the value(s) "project_setup", "review_variants", or "all"')

  # Determine which task types to return
  types = None
  if args.types:
    types_list = args.types.split(',') if ',' in args.types else [args.types]
    for task_type in type_list:
      if task_type == 'set_project_attribute_value':
        types.append(task_type)
      elif task_type == 'add_files_for_samples':
        types.append(task_type)
      elif task_type == 'primary_clinvar_review':
        types.append(task_type)
      elif task_type == 'submit_for_processing':
        types.append(task_type)
      elif category == 'all':
        task_type.append('set_project_attribute_value')
        task_type.append('add_files_for_samples')
        task_type.append('primary_clinvar_review')
        task_type.append('submit_for_processing')
      else:
        fail('--types / -t must take the value(s) "set_project_attribute_value", "add_files_for_samples", "primary_clinvar_review", "submit_for_processing", or "all"')

  # Determine which tasks to return based on completed status
  completed = None
  if args.completed:
    if args.completed == 'completed':
      completed = 'true'
    elif args.completed == 'pending':
      completed = 'false'
    elif args.completed == 'all':
      completed = None
    else:
      fail('--completed / -m must take the value "completed", "pending", or "all"')

  # Get the list of project ids to check
  project_ids = None
  if args.project_ids:
    project_ids = args.project_ids.split(',') if ',' in args.project_ids else [args.project_ids]

  # Get the requested tasks
  for task in api_mosaic.get_tasks(categories = categories, completed = completed, project_ids = project_ids, types = types, order_dir=None):
    pprint(task)

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

  # Filter tasks by category
  parser.add_argument('--categories', '-g', required = False, metavar = 'string', help = 'A comma separated list of types to return. The values "all", "project_setup", or "review_variants" can be used. Default: all')

  # Filter tasks by type
  parser.add_argument('--types', '-t', required = False, metavar = 'string', help = 'A comma separated list of types to return. The values "all", "set_project_attribute_value", "add_files_for_samples", "primary_clinvar_review", and "submit_for_processing" can be used. Default: all')

  # Only return completed tasks
  parser.add_argument('--completed', '-m', required = False, metavar = 'string', help = 'Return "completed", "pending", or "all" tasks. Default: all')

  # Project ids to check
  parser.add_argument('--project_ids', '-p', required = False, metavar = 'string', help = 'A comma separated list of project ids to check')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
