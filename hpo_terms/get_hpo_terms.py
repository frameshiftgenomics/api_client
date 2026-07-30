import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Put the hpo terms in a list
  hpo_terms = args.hpo_terms.split(',') if ',' in args.hpo_terms else [args.hpo_terms]
  for hpo in api_mosaic.get_hpo_terms(hpo_terms):
    print(hpo)

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The hpo_terms to get the ids for
  parser.add_argument('--hpo_terms', '-t', required = True, metavar = 'string', help = 'A comma separated list of the HPO terms to get the Mosaic ids for')

  return parser.parse_args()

if __name__ == "__main__":
  main()
