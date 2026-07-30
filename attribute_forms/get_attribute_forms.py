import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Get all public attributes
  attributes = {}
  for attribute in api_mosaic.get_public_project_attributes():
    attributes[attribute['id']] = {'name': attribute['name'], 'uid': attribute['uid']}

  # If a form is specified, set the is_display to False
  is_display = False if args.form_id else True
  is_terminate = False

  # Get all of the attribute forms
  data = api_mosaic.get_attribute_forms()
  for form in data['data']:
    if args.form_id:
      if int(args.form_id) == int(form['id']):
        is_display = True
        is_terminate = True
    if is_display:
      print(form['name'], ': ', form['id'], ' (', form['origin_type'], ')', sep = '')
      if args.display_all:
        for attribute in form['attribute_form_attributes']:
          print('  ', attribute['attribute_id'], ': ', attributes[attribute['attribute_id']]['name'], ', ', attribute['type'], sep = '')
    if is_terminate:
      exit(0)

# Input options
def parse_command_line():
  parser, groups = base_parser()
  optional_arguments = groups.optional
  display_arguments = groups.display

  # Choose a specific attribute form
  optional_arguments.add_argument('--form_id', '-f', required = False, metavar = 'integer', help = 'The id of the form to get')

  # Verbose output
  display_arguments.add_argument('--display_all', '-da', required = False, action = 'store_true', help = 'Verbose output')

  return parser.parse_args()

if __name__ == "__main__":
  main()
