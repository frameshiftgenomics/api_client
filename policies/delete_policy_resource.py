import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Create the project object
  project = api_mosaic.get_project(args.project_id)

  # Check the resource type to be deleted is valid
  allowed_types = ['project_attribute',
                   'project_conversation']
  resource_type = args.resource_type if args.resource_type in allowed_types else fail('Unknown resource type') 

  # Delete the policy resource
  project.delete_policy_resource(args.policy_id, resource_type)

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The project id 
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id')

  # The policy id to post attributes to
  parser.add_argument('--policy_id', '-i', required = True, metavar = 'integer', help = 'The policy id to post attributes to')

  # The type or resource to delete and the id of the resource
  parser.add_argument('--resource_type', '-t', required = True, metavar = 'string', help = 'The resource type to dekete: project_attribute, project_conversation')
  parser.add_argument('--resource_id', '-r', required = True, metavar = 'integer', help = 'The id of the resource to delete')

  return parser.parse_args()

if __name__ == "__main__":
  main()
