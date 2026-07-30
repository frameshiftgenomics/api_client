import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Determine which tasks to return based on categories
  categories = []
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
  types = []
  if args.types:
    types_list = args.types.split(',') if ',' in args.types else [args.types]
    for task_type in types_list:
      if task_type == 'set_project_attribute_value':
        types.append(task_type)
      elif task_type == 'add_files_for_samples':
        types.append(task_type)
      elif task_type == 'primary_clinvar_review':
        types.append(task_type)
      elif task_type == 'submit_for_processing':
        types.append(task_type)
      elif task_type == 'all':
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
  project_ids = []
  if args.project_ids:
    project_ids = args.project_ids.split(',') if ',' in args.project_ids else [args.project_ids]

  # Check for mututally exclusive options
  flag_list = (args.ids_only, args.raw_output)
  if sum(flag_list) > 1:
    fail('multiple flags to get default, latest etc are set. These flags are mutually exclusive')

  # Get the requested tasks
  for task in api_mosaic.get_tasks(categories = categories, completed = completed, project_ids = project_ids, types = types, order_dir=None):
    if args.raw_output:
      pprint(task)
    elif args.ids_only:
      print(task['id'])
    else:
      print('id: ', task['id'], sep = '')
      print('  category: ', task['category'], sep = '')
      print('  task_type: ', task['type'], sep = '')

# Input options
def parse_command_line():
  parser, groups = base_parser()
  optional_arguments = groups.optional
  display_arguments = groups.display

  # Filter tasks by category
  optional_arguments.add_argument('--categories', '-g', required = False, metavar = 'string', help = 'A comma separated list of types to return. The values "all", "project_setup", or "review_variants" can be used. Default: all')

  # Filter tasks by type
  optional_arguments.add_argument('--types', '-t', required = False, metavar = 'string', help = 'A comma separated list of types to return. The values "all", "set_project_attribute_value", "add_files_for_samples", "primary_clinvar_review", and "submit_for_processing" can be used. Default: all')

  # Only return completed tasks
  optional_arguments.add_argument('--completed', '-m', required = False, metavar = 'string', help = 'Return "completed", "pending", or "all" tasks. Default: all')

  # Project ids to check
  optional_arguments.add_argument('--project_ids', '-p', required = False, metavar = 'string', help = 'A comma separated list of project ids to check')

  # Display arguments
  display_arguments.add_argument('--raw_output', '-ro', required = False, action = 'store_true', help = 'Output the raw data objects returned by the api')
  display_arguments.add_argument('--ids_only', '-io', required = False, action = 'store_true', help = 'Only output the project ids')

  return parser.parse_args()

if __name__ == "__main__":
  main()
