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

  # Get any attribute_ids or conversation_ids
  attribute_id = args.attribute_id if args.attribute_id else None
  conversation_id = args.conversation_id if args.conversation_id else None
  if not attribute_id and not conversation_id:
    fail('An attribute or conversation id must be provided')

  # Post the attribute to the policy
  project.post_policy_project_resource(args.policy_id, attribute_id = attribute_id, conversation_id = conversation_id)

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  required_arguments = groups.required
  optional_arguments = groups.optional

  # The project id 
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id')

  # The policy id to post attributes to
  required_arguments.add_argument('--policy_id', '-i', required = True, metavar = 'integer', help = 'The policy id to post attributes to')

  # The attribute id to post to the policy
  optional_arguments.add_argument('--attribute_id', '-t', required = False, metavar = 'integer', help = 'The attribute id to post to the policy')
  optional_arguments.add_argument('--conversation_id', '-v', required = False, metavar = 'integer', help = 'The conversation id to post to the policy')

  return parser.parse_args()

if __name__ == "__main__":
  main()
