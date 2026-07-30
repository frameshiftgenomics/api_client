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
  try:
    project = api_mosaic.get_project(args.project_id)
  except Exception as e:
    fail('Failed to open project. Error was: ' + str(e))

  # Set the name, nickname and description
  name = args.name if args.name else None
  nickname = args.nickname if args.nickname else None
  description = args.description if args.description else None

  # If the primary_sample_id is given, check this sample is in the project
  primary_sample_id = None
  if args.primary_sample_id:
    has_sample_id = False
    for sample in project.get_samples():
      if int(sample['id']) == int(args.primary_sample_id):
        has_sample_id = True
        break
    if not has_sample_id:
      fail('supplied primary sample id is not the id of a sample in the project')
    else:
      primary_sample_id = args.primary_sample_id 

  # PUT the updates
  try:
    project.put_project(name = name, nickname = nickname, description = description, primary_sample_id = primary_sample_id)
  except Exception as e:
    fail('failed to PUT project updates. Error wes: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  optional_arguments = groups.optional

  # The project id
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # Optional arguments
  optional_arguments.add_argument('--name', '-n', required = False, metavar = 'string', help = 'The name of the new data group view')
  optional_arguments.add_argument('--nickname', '-nn', required = False, metavar = 'string', help = 'The nickname of the new data group view')
  optional_arguments.add_argument('--description', '-d', required = False, metavar = 'string', help = 'A description of the new data group view')
  optional_arguments.add_argument('--primary_sample_id', '-s', required = False, metavar = 'integer', help = 'The id of the project sample to be designated as primary. Typically this is the id of the proband')

  return parser.parse_args()

if __name__ == "__main__":
  main()
