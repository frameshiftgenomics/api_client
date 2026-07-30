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

  # Build the coordinates of the variant
  chromosome = args.chromosome.replace('chr', '') if 'chr' in args.chromosome else args.chromosome
  variant_position = str(chromosome) + ':' + str(args.position)
  print(project.get_variant_by_position(variant_position))

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to add variant filters to')

  # Get the chromosome and coordiante of the variant
  parser.add_argument('--chromosome', '-r', required = True, metavar = 'string', help = 'The chromosome, the variant is on')
  parser.add_argument('--position', '-o', required = True, metavar = 'integer', help = 'The variants position')

  return parser.parse_args()

if __name__ == "__main__":
  main()
