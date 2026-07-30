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

  # Delete the file
  project.post_sample_file(args.sample_id, url=args.endpoint_url, experiment_id=args.experiment_id, library_type=args.library_type, name=args.name, nickname=args.nickname, qc=args.qc, reference=args.reference, file_type=args.file_type, size=args.size, uri=args.uri, vcf_sample_name=args.vcf_sample_name)

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required
  optional_arguments = groups.optional

  # The project and sample ids to which the file is to be added are required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')
  project_arguments.add_argument('--sample_id', '-s', required = True, metavar = 'integer', help = 'The sample id of the sample the file is to be attached to')

  # Required arguments related to the file to add
  required_arguments.add_argument('--name', '-n', required = True, metavar = 'string', help = 'The name of the file to add')
  required_arguments.add_argument('--reference', '-r', required = True, metavar = 'string', help = 'The reference genome of the project')
  required_arguments.add_argument('--file_type', '-t', required = True, metavar = 'string', help = 'The file type of the file being added (e.g. vcf)')
  required_arguments.add_argument('--uri', '-u', required = True, metavar = 'string', help = 'The location of the file being added')

  # Optional arguments related to the file to add
  optional_arguments.add_argument('--nickname', '-k', required = False, metavar = 'string', help = 'The nickname of the file to add')
  optional_arguments.add_argument('--endpoint_url', '-d', required = False, metavar = 'string', help = 'The id of the experiment this file should be added to')
  optional_arguments.add_argument('--experiment_id', '-e', required = False, metavar = 'integer', help = 'The id of the experiment this file should be added to')
  optional_arguments.add_argument('--library_type', '-l', required = False, metavar = 'string', help = 'The library type of the sequencing data')
  optional_arguments.add_argument('--qc', '-q', required = False, metavar = 'json', help = 'Json file containing qc information for the file')
  optional_arguments.add_argument('--size', '-z', required = False, metavar = 'integer', help = 'The size in bytes of the file')
  optional_arguments.add_argument('--vcf_sample_name', '-v', required = False, metavar = 'string', help = 'The sample identifier in the vcf file')

  return parser.parse_args()

if __name__ == "__main__":
  main()
