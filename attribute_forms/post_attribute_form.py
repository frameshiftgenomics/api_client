import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Build the json object
  attributes_json = []
  if args.required_attributes:
    attributes = args.required_attributes.split(',')
    for attribute_id in attributes:
      attributes_json.append({'attribute_id':
        int(attribute_id), 'type': 'required'})
  if args.suggested_attributes:
    attributes = args.suggested_attributes.split(',')
    for attribute_id in attributes:
      attributes_json.append({'attribute_id':
        int(attribute_id), 'type': 'suggested'})
  if args.optional_attributes:
    attributes = args.optional_attributes.split(',')
    for attribute_id in attributes:
      attributes_json.append({'attribute_id':
        int(attribute_id), 'type': 'optional'})

  if len(attributes_json) == 0:
    print('WARNING: No attributes added - no attribute form created')
    exit(0)

  # Check if an origin_type is defined
  origin_types = ['institutional', 'user']
  origin_type = None
  if args.origin_type:
    if args.origin_type not in origin_types:
      fail('Unknown origin type')
    origin_type = args.origin_type

  # Post an attribute form
  data = api_mosaic.post_attribute_form(name = args.name, attributes = attributes_json, origin_type = origin_type)

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # Required arguments
  parser.add_argument('--name', '-n', required = True, metavar = 'string', help = 'The name of the attribute form')

  # The type of form (institutional or user)
  parser.add_argument('--origin_type', '-t', required = False, metavar = 'string', help = 'The origin_type: institutional or user')

  # Optional arguments
  parser.add_argument('--required_attributes', '-r', required = False, metavar = 'string', help = 'A comma separated list of the ids of all required attributes')
  parser.add_argument('--suggested_attributes', '-s', required = False, metavar = 'string', help = 'A comma separated list of the ids of all suggested attributes')
  parser.add_argument('--optional_attributes', '-o', required = False, metavar = 'string', help = 'A comma separated list of the ids of all optional attributes')

  return parser.parse_args()

if __name__ == "__main__":
  main()
