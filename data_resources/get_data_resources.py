import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Get the resources information
  for resource in api_mosaic.get_data_resources():
    if args.raw_output:
      pprint(resource)
    elif args.clinvar_grch38:
      if resource['uid'] == 'clinvar_grch38':
        print(resource['download_url'])
        exit(0)
    elif args.clinvar_grch37:
      if resource['uid'] == 'clinvar_grch37':
        print(resource['download_url'])
        exit(0)
    else:
      print(resource['name'], ', version: ', resource['version'], sep = '')

# Input options
def parse_command_line():
  parser, groups = base_parser()
  display_arguments = groups.display

  # Get the latest ClinVar version
  display_arguments.add_argument('--clinvar_grch38', '-cv', required = False, action = 'store_true', help = 'If set, get the download link for the latest GRCh38 ClinVar version')
  display_arguments.add_argument('--clinvar_grch37', '-cvo', required = False, action = 'store_true', help = 'If set, get the download link for the latest GRCh37 ClinVar version')

  # Dump the raw data object
  display_arguments.add_argument('--raw_output', '-ro', required = False, action = 'store_true', help = 'If set, dump the json object as output from Mosaic')

  return parser.parse_args()

if __name__ == "__main__":
  main()
