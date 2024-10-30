import os
import argparse

from pprint import pprint
from sys import path

def main():

  # Parse the command line
  args = parse_command_line()

  # Import the api client
  path.append(args.api_client)
  from mosaic import Mosaic, Project, Store
  api_store = Store(config_file = args.client_config)
  api_mosaic = Mosaic(config_file = args.client_config)

  # Get all public attributes
  attributes = {}
  for attribute in api_mosaic.get_public_project_attributes():
    attributes[attribute['id']] = {'name': attribute['name'], 'uid': attribute['uid']}

  # Get all of the attribute forms
  data = api_mosaic.get_attribute_forms()
  for form in data['data']:
    print(form['name'], ': ', form['id'], sep = '')
    for attribute in form['attribute_form_attributes']:
      print('  ', attribute['attribute_id'], ': ', attributes[attribute['attribute_id']]['name'], ', ', attribute['type'], sep = '')

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = True, metavar = 'string', help = 'The api_client directory')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print(message, sep = "")
  exit(1)

if __name__ == "__main__":
  main()
