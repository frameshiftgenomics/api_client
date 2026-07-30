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

  # Loop over the samples in the project and delete them all
  for sample in project.get_samples():

    # Delete the sample
    try:
      project.delete_sample(sample['id'])
    except:
      fail('Unable to delete sample with id ' + str(sample['id']))
 
# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  return parser.parse_args()

if __name__ == "__main__":
  main()
