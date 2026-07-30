import os
import sys
import time

from datetime import datetime
from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # Delete the instance
  try:
    project.delete_task(args.task_id)
  except Exception as e:
    fail('Failed to delete task with the error ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')
  project_arguments.add_argument('--task_id', '-t', required = True, metavar = 'integer', help = 'The Mosaic id of the task to delete')

  return parser.parse_args()

if __name__ == "__main__":
  main()
