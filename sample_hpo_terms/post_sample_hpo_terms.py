import os
import sys

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
    fail('Failed to open a project with the given id')

  # Check the HPO terms are valid
  hpo_ids = args.hpo_ids.split(',')

  # Parse the sources into an array of strings
  sources = args.sources.split(',') if args.sources else []

  # Post the HPO terms to the sample
  for hpo_id in hpo_ids:
    try:
      project.post_sample_hpo_term(args.sample_id, hpo_id, sources = sources)
    except Exception as e:
      print('Failed to POST the following HPO term (this will occur if the term is already present for the sample): ', str(hpo_id), '. Error was: ' + str(e), sep = '')

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required
  optional_arguments = groups.optional

  # Get the id of the project and the sample whose HPO terms are required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The project id')
  project_arguments.add_argument('--sample_id', '-s', required = True, metavar = 'integer', help = 'The id of the sample whose HPO terms are required')

  # A list of HPO terms to add
  required_arguments.add_argument('--hpo_ids', '-i', required = True, metavar = 'string', help = 'A comma separated list of terms in the format HP:00001,HP:00002')

  # Optional arguments
  optional_arguments.add_argument('--sources', '-so', required = False, metavar = 'string', help = 'A comma separatd list of sources to assign to the HPO terms')

  return parser.parse_args()

if __name__ == "__main__":
  main()
