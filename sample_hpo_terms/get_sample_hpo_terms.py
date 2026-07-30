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
    fail('Failed to open project. Error was: ' + str(e))

  # If the terms should be output for Exomiser, collect them in a list first
  if args.exomiser_format:
    hpo_terms = []
    for hpo_term in project.get_sample_hpo_terms(args.sample_id):
      hpo_terms.append(hpo_term['hpo_id'])
    print(hpo_terms)

  # Get the HPO terms for the sample
  else:
    for hpo_term in project.get_sample_hpo_terms(args.sample_id):
      print(hpo_term['hpo_id'], ': ', hpo_term['label'], ' (id: ', hpo_term['id'], ')', sep = '')

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project

  # Get the id of the project and the sample whose HPO terms are required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The project id')
  project_arguments.add_argument('--sample_id', '-s', required = True, metavar = 'integer', help = 'The id of the sample whose HPO terms are required')

  # Output in a format for exomiser
  project_arguments.add_argument('--exomiser_format', '-e', required = False, action = 'store_true', help = 'Output the HPO terms in a format useful for Exomiser')

  return parser.parse_args()

if __name__ == "__main__":
  main()
