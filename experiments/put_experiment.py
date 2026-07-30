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
  project.put_experiment(args.experiment_id, name = args.name, description = description, experiment_type = experiment_type, file_ids = file_ids)

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # the project id
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The mosaic project id')

  # the experiment id to update
  parser.add_argument('--experiment_id', '-e', required = True, metavar = 'integer', help = 'The id of the experiment to update')

  # The things to add to the experiment
  parser.add_argument('--name', '-n', required = False, metavar = 'string', help = 'The name of the experiment to create')
  parser.add_argument('--description', '-d', required = False, metavar = 'string', help = 'An optional description of the experiment')
  parser.add_argument('--experiment_type', '-t', required = False, metavar = 'string', help = 'An optional type, e.g. WGS, RNA')
  parser.add_argument('--file_ids', '-f', required = False, metavar = 'integer', help = 'An optional (but recommended) comma separated list of file ids to add to the experiment')

  return parser.parse_args()

if __name__ == "__main__":
  main()
