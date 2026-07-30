import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Check that the task type id is valid
  if int(args.task_type_id) > 4:
    fail('The task type id supplied is not valid. Please select an integer between 1 and 4')

  # Open an api client project object for the defined project
  try:
    project = api_mosaic.get_project(args.project_id)
  except Exception as e:
    fail('Failed to open requested project. Error was: ' + str(e))

  # Check if this is a collection
  is_collection = False
  if project.get_project()['is_collection']:
    is_collection = True

  # The cascade option is only available for collections
  if args.cascade and not is_collection:
    fail('The flag to cascade is set, but the supplied project id is not for a collection')

  # Set the array of attribute ids
  attribute_ids = None
  if args.attribute_ids:
    attribute_ids = args.attribute_ids.split(',') if args.attribute_ids else [args.attribute_ids]

  # Apply the attributes
  try:
    project.put_task_type_attributes(args.task_type_id, attribute_ids = attribute_ids, cascade_update = args.cascade)
  except Exception as e:
    fail('Failed to apply task type attributes. Error was: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required
  optional_arguments = groups.optional

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # The task type to apply the attributes to
  project_arguments.add_argument('--task_type_id', '-t', required = True, metavar = 'integer', help = 'The id of the task type (e.g. 4: Primary ClinVar Review). Tasks created for this type will include the supplied attributes in the Tasks view')

  # A list of attribute ids to add to the tasks
  required_arguments.add_argument('--attribute_ids', '-i', required = True, metavar = 'string', help = 'A comma separated list of attribute ids to add to the task types')

  # A list of attribute ids to add to the tasks
  optional_arguments.add_argument('--cascade', '-ca', required = False, action = 'store_true', help = 'If set, the attributes will be cascaded to all sub-projects')

  return parser.parse_args()

if __name__ == "__main__":
  main()
