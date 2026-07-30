import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Get
  project = api_mosaic.get_project(34)
  project_by_site = {}
  for attribute in project.get_project_attributes():
    if attribute['name'] == 'Clinical Site':
      for udn_project in attribute['values']:
        project_by_site[udn_project['project_id']] = udn_project['value']

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
  tasks = {}
  for task in api_mosaic.get_tasks(categories = categories, completed = completed, project_ids = project_ids, types = types, order_dir=None):
    if task['project_id'] not in tasks:
      tasks[task['project_id']] = 1
    else:
      tasks[task['project_id']] += 1

  # Sort the tasks by site
  tasks_by_site = {}
  for project_id in tasks:
    site = project_by_site[project_id]
    if site not in tasks_by_site:
      tasks_by_site[site] = {'count': 1, 'genes': []}
    else:
      tasks_by_site[site]['count'] += 1

    # Get information on the variant
    project = api_mosaic.get_project(project_id)
    for variant_set in project.get_variant_sets():
      if variant_set['name'].startswith('ClinVar') and 'Primary' in variant_set['name']:
        variant_set_id = variant_set['id']
        variant_set_info = project.get_variant_set(variant_set_id, include_variant_data = 'true')
        for variant_id in variant_set_info['variant_ids']:
          variant_info = project.get_variant(variant_id, include_annotation_data = 'true')
          for gene in variant_info['gene_name@default']:
            tasks_by_site[site]['genes'].append(gene)

  # Print out the results
  for site in tasks_by_site:
    print(site, tasks_by_site[site]['count'])
    print(','.join(tasks_by_site[site]['genes']))

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # Filter tasks by category
  parser.add_argument('--categories', '-g', required = False, metavar = 'string', help = 'A comma separated list of types to return. The values "all", "project_setup", or "review_variants" can be used. Default: all')

  # Filter tasks by type
  parser.add_argument('--types', '-t', required = False, metavar = 'string', help = 'A comma separated list of types to return. The values "all", "set_project_attribute_value", "add_files_for_samples", "primary_clinvar_review", and "submit_for_processing" can be used. Default: all')

  # Only return completed tasks
  parser.add_argument('--completed', '-m', required = False, metavar = 'string', help = 'Return "completed", "pending", or "all" tasks. Default: all')

  # Project ids to check
  parser.add_argument('--project_ids', '-p', required = False, metavar = 'string', help = 'A comma separated list of project ids to check')

  return parser.parse_args()

if __name__ == "__main__":
  main()
