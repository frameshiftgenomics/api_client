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

  try:
    project.put_project_attributes(args.attribute_id, value = args.value)
  except:
    try:
      project.post_project_attribute(value = args.value)
    except Exception as e:
      fail('Could not update attribute. Error: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required

  # The project id to which the filter is to be added is required
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')
  project_arguments.add_argument('--attribute_id', '-i', required = True, metavar = 'integer', help = 'The Mosaic attribute id to update')
  required_arguments.add_argument('--value', '-v', required = False, metavar = 'string', help = 'The value of the attribute')

  return parser.parse_args()

if __name__ == "__main__":
  main()
