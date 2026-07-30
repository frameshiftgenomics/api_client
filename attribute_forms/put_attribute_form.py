import json
import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Build the json object
  attributes_json = []
  stored_attributes = []
  if args.required_attributes:
    attributes = args.required_attributes.split(',') if ',' in args.required_attributes else [args.required_attributes]
    for attribute_id in attributes:
      attributes_json.append({'attribute_id': int(attribute_id), 'type': 'required'})
      stored_attributes.append(int(attribute_id))
  if args.suggested_attributes:
    attributes = args.suggested_attributes.split(',') if ',' in args.suggested_attributes else [args.suggested_attributes]
    for attribute_id in attributes:
      attributes_json.append({'attribute_id': int(attribute_id), 'type': 'suggested'})
      stored_attributes.append(int(attribute_id))
  if args.optional_attributes:
    attributes = args.optional_attributes.split(',') if ',' in args.optional_attributes else [args.optional_attributes]
    for attribute_id in attributes:
      attributes_json.append({'attribute_id': int(attribute_id), 'type': 'optional'})
      stored_attributes.append(int(attribute_id))

  # Get all available attribute forms
  attribute_form_id = False
  for attribute_form in api_mosaic.get_attribute_forms()['data']:
    if str(attribute_form['id']) == str(args.attribute_form_id):

      # Update the form name
      name = args.name if args.name else attribute_form['name']
      attribute_form_id = int(attribute_form['id'])

      # Handle the attributes if the retain attribute flag is set
      if args.retain_existing_attributes:
        for attribute in attribute_form['attribute_form_attributes']:

          # If the attribute is in stored_attributes it was updated by the user, so it is already in the
          # json and can be ignored
          if int(attribute['attribute_id']) not in stored_attributes:
            attributes_json.append({'attribute_id': attribute['attribute_id'], 'type': attribute['type']})

  # Fail if the given attribute id does not exist
  if not attribute_form_id:
    fail('no attribute form with the given id')
  print('Updating attribute form: ', str(name), '...', sep = '', end = '')

  # Remove amy requested attributes from the form
  attributes = []
  if args.remove_attributes:
    attributes = args.remove_attributes.split(',') if ',' in args.remove_attributes else [args.remove_attributes]
  updated_attributes_json = []
  for attribute in attributes_json:
    if str(attribute['attribute_id']) not in attributes:
      updated_attributes_json.append(attribute)

  # Post an attribute form
  data = api_mosaic.put_attribute_form(attribute_form_id, name = name, attributes = updated_attributes_json)
  print('complete')

# Input options
def parse_command_line():
  parser, groups = base_parser()
  required_arguments = groups.required
  optional_arguments = groups.optional

  # Required arguments
  required_arguments.add_argument('--attribute_form_id', '-i', required = True, metavar = 'string', help = 'The id of the attribute form to update')

  # Optional arguments
  optional_arguments.add_argument('--name', '-n', required = False, metavar = 'string', help = 'The name of the attribute form')
  optional_arguments.add_argument('--required_attributes', '-r', required = False, metavar = 'string', help = 'A comma separated list of the ids of all required attributes')
  optional_arguments.add_argument('--suggested_attributes', '-s', required = False, metavar = 'string', help = 'A comma separated list of the ids of all suggested attributes')
  optional_arguments.add_argument('--optional_attributes', '-o', required = False, metavar = 'string', help = 'A comma separated list of the ids of all optional attributes')
  optional_arguments.add_argument('--remove_attributes', '-m', required = False, metavar = 'string', help = 'A comma separated list of the ids of all attributes to be removed from the form')
  optional_arguments.add_argument('--retain_existing_attributes', '-re', required = False, action = 'store_true', help = 'If set, no existing attributes will be removed from the attribute form - only new ones will be added')

  return parser.parse_args()

if __name__ == "__main__":
  main()
