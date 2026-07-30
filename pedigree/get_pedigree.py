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

  # If the ped file is required, print this information
  if args.output_ped:
    samples = {}
    for sample in project.get_samples():
      pedigree = sample['pedigree']
      if pedigree:
        samples[sample['id']] = {'name': sample['name'],
                               'maternal_id': pedigree['maternal_id'],
                               'paternal_id': pedigree['paternal_id'],
                               'sex': pedigree['sex'],
                               'kindred_name': pedigree['kindred_name'],
                               'affection_status': pedigree['affection_status']}
      else:
        samples[sample['id']] = {'name': sample['name'],
                               'maternal_id': None,
                               'paternal_id': None,
                               'sex': None,
                               'kindred_name': None,
                               'affection_status': None}

    # Write out the ped
    for sample in samples:
      kindred_name = samples[sample]['kindred_name']
      sex = samples[sample]['sex']
      affection_status = samples[sample]['affection_status']
      maternal_id = samples[sample]['maternal_id']
      maternal_name = samples[maternal_id]['name'] if maternal_id else '0'
      paternal_id = samples[sample]['paternal_id']
      paternal_name = samples[paternal_id]['name'] if paternal_id else '0'
      print(samples[sample]['kindred_name'], samples[sample]['name'], paternal_name, maternal_name, sex, affection_status, sep = '\t')

    # Get the pedigree
  else:
    for pedigree in project.get_pedigree(args.sample_id):
      pprint(pedigree)

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required
  display_arguments = groups.display

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to add variant filters to')

  # The sample id of the sample to get the pedigree for
  required_arguments.add_argument('--sample_id', '-s', required = True, metavar = 'integer', help = 'The sample id of the sample whose pedigree is to be retrieved')

  # Output a ped file
  display_arguments.add_argument('--output_ped', '-op', required = False, action = 'store_true', help = 'Output a ped file')

  return parser.parse_args()

if __name__ == "__main__":
  main()
