import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # Set up the experiment information
  description = args.description if args.description else None
  experiment_type = args.experiment_type if args.experiment_type else None
  if args.file_ids:
    file_ids = args.file_ids.split(',') if ',' in args.file_ids else [args.file_ids]
  else:
    file_ids = None

  # Create the new experiment
  project.post_experiment(name = args.name, description = description, experiment_type = experiment_type, file_ids = file_ids)

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required
  optional_arguments = groups.optional

  # The project id
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id')

  # The things to add to the experiment
  required_arguments.add_argument('--name', '-n', required = True, metavar = 'string', help = 'The name of the experiment to create')
  required_arguments.add_argument('--file_ids', '-f', required = False, metavar = 'integer', help = 'An optional (but recommended) comma separated list of file ids to add to the experiment')
  optional_arguments.add_argument('--description', '-d', required = False, metavar = 'string', help = 'An optional description of the experiment')
  optional_arguments.add_argument('--experiment_type', '-t', required = False, metavar = 'string', help = 'An optional type, e.g. WGS, RNA')

  return parser.parse_args()

if __name__ == "__main__":
  main()
