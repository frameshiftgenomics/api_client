import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  try:
    project = api_mosaic.get_project(args.project_id)
  except Exception as e:
    fail('failed to open project. Error was: ' + str(e))

  # Check that the maternal or paternal samples exist in the project
  samples = []
  maternal_id = None
  paternal_id = None
  if args.maternal_id or args.paternal_id:

    if args.maternal_id == args.paternal_id:
      fail('maternal_id and paternal_id cannot be the same')
    for sample in project.get_samples():
      samples.append(int(sample['id']))
    if args.maternal_id:
      if int(args.maternal_id) not in samples:
        fail('unknown sample id for mother')
      else:
        maternal_id = args.maternal_id
    if args.paternal_id:
      if int(args.paternal_id) not in samples:
        fail('unknown sample id for father')
      else:
        paternal_id = args.paternal_id

  # Set the affaction status and sex
  affection_status = 2 if args.affection_status else 1
  sex = 0
  if args.sex:
    if args.sex == 'Male' or args.sex == 'male' or args.sex == 'm' or args.sex == 'M':
      sex = 1
    elif args.sex == 'Female' or args.sex == 'female' or args.sex == 'f' or args.sex == 'F':
      sex = 2
    else:
      fail('unknown biolgical sex')

  # Post the pedigree
  try:
    project.put_pedigree(args.sample_id, maternal_id = maternal_id, paternal_id = paternal_id, affection_status = affection_status, sex = sex)
  except Exception as e:
    fail('failed to post pedigree. Error was: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  optional_arguments = groups.optional

  # The project and sample ids
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id')
  project_arguments.add_argument('--sample_id', '-s', required = True, metavar = 'integer', help = 'The Mosaic sample id')

  # Additional pedigree information
  optional_arguments.add_argument('--maternal_id', '-mi', required = False, metavar = 'integer', help = 'The sample id of the mother.')
  optional_arguments.add_argument('--paternal_id', '-pi', required = False, metavar = 'integer', help = 'The sample id of the father.')
  optional_arguments.add_argument('--affection_status', '-as', required = False, action = 'store_true', help = 'Set if the sample is affected')
  optional_arguments.add_argument('--sex', '-x', required = False, metavar = 'string', help = 'The biological sex of the sample. Male or Female')

  return parser.parse_args()

if __name__ == "__main__":
  main()
