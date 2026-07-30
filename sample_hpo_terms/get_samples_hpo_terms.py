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
  project = api_mosaic.get_project(args.project_id)

  # Get the HPO terms for the sample
  sample_hpo = {}
  for hpo_term in project.get_samples_hpo_terms():
    sample_id = hpo_term['sample_id']
    if sample_id not in sample_hpo:
      sample_hpo[sample_id] = {}
    sample_hpo[sample_id][hpo_term['id']] = {'label': hpo_term['label'], 'id': hpo_term['id']}

  # Get the names of all the samples
  samples = {}
  for sample in project.get_samples():
    samples[sample['id']] = sample['name']
  for sample_id in sample_hpo:
    print('sample: ', samples[sample_id], ' (', sample_id, ')', sep = '')
    for hpo_id in sample_hpo[sample_id]:
      print('  ', hpo_id, ': ', sample_hpo[sample_id][hpo_id]['label'], ' (id: ', sample_hpo[sample_id][hpo_id]['id'], ')', sep = '')

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project

  # Get the id of the project
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The project id')

  return parser.parse_args()

if __name__ == "__main__":
  main()
