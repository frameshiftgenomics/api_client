import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Get the project settings
  api_mosaic.delete_job(args.job_id)

# Input options
def parse_command_line():
  parser, groups = base_parser()
  required_arguments = groups.required

  # The job id to query
  required_arguments.add_argument('--job_id', '-j', required = True, metavar = 'integer', help = 'The Mosaic redis job is to get the status of')

  return parser.parse_args()

if __name__ == "__main__":
  main()
