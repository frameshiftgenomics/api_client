import argparse
import json
import os

from sys import path

def main():

  # Parse the command line
  args = parse_command_line()

  # If the api_client path was not specified, get it from the script path
  if not args.api_client:
    try:
      args.api_client = os.path.dirname(os.path.realpath(__file__)).split('api_client')[0] + str('api_client')
    except:
      fail('Could not get the api_client path from the command. Please specify using --api_client / -a')

  # Import the api client
  path.append(args.api_client)
  try: 
    from mosaic import Mosaic, Project, Store
  except:
    fail('Cannot find mosaic. Please set the --api_client / -a argument')
  api_store = Store(config_file = args.client_config)
  api_mosaic = Mosaic(config_file = args.client_config)

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
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

  # Required arguments
  parser.add_argument('--name', '-n', required = True, metavar = 'string', help = 'The name of the attribute form')

  # The type of form (institutional or user)
  parser.add_argument('--origin_type', '-t', required = False, metavar = 'string', help = 'The origin_type: institutional or user')

  # Optional arguments
  parser.add_argument('--required_attributes', '-r', required = False, metavar = 'string', help = 'A comma separated list of the ids of all required attributes')
  parser.add_argument('--suggested_attributes', '-s', required = False, metavar = 'string', help = 'A comma separated list of the ids of all suggested attributes')
  parser.add_argument('--optional_attributes', '-o', required = False, metavar = 'string', help = 'A comma separated list of the ids of all optional attributes')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
