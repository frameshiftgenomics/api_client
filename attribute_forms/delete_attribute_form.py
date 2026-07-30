import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Delete the attribute form
  api_mosaic.delete_attribute_form(args.attribute_form_id)

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The id of the attribute form to delete
  parser.add_argument('--attribute_form_id', '-i', required = True, metavar = 'string', help = 'The id of the attribute form to delete')

  return parser.parse_args()

if __name__ == "__main__":
  main()
