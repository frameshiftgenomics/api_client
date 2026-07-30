import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Check that the reference is valid
  allowed_references = ['GRCh37', 'GRCh38']
  if args.reference not in allowed_references:
    fail('unknown reference')

  # Check the privacy level is allowed
  allowed_privacy = ['public', 'protected', 'private']
  args.privacy_level = 'private' if not args.privacy_level else args.privacy_level
  if args.privacy_level not in allowed_privacy:
    fail('unknown privacy level')
  
  # If collection_projects is set, make sure the is_collection is also set
  collection_projects = None
  if args.collection_projects:
    if not args.is_collection:
      fail('A list of project ids to add to the collection is provided. To create a collection, the --is_collection (-co) must be set')
    collection_projects = args.collection_projects.split(',') if ',' in args.collection_projects else [args.collection_projects]

  # If attribute forms are listed
  attribute_forms = []
  if args.attribute_forms:
    for attribute_form_id in args.attribute_forms.split(','):
      attribute_forms.append({"form_id": attribute_form_id, "attribute_form_attributes": []})

  ped_file = args.ped_file if args.ped_file else None
  family_name = args.family_name if args.family_name else None

  # Create a project
  project = api_mosaic.post_project(args.name, \
                                    args.reference, \
                                    nickname = args.nickname, \
                                    description = args.description, \
                                    family_name = args.family_name, \
                                    ped_file = ped_file, \
                                    is_collection = args.is_collection, \
                                    collection_projects = collection_projects, \
                                    privacy_level = args.privacy_level, \
                                    template_project_id = args.template_project_id, \
                                    attribute_forms = attribute_forms)

# Input options
def parse_command_line():
  parser, groups = base_parser()
  required_arguments = groups.required
  optional_arguments = groups.optional

  # The project information
  required_arguments.add_argument('--name', '-n', required = True, metavar = 'string', help = 'The project name')
  required_arguments.add_argument('--reference', '-r', required = True, metavar = 'string', help = 'The project reference')
  optional_arguments.add_argument('--nickname', '-m', required = False, metavar = 'string', help = 'The project nickname')
  optional_arguments.add_argument('--description', '-d', required = False, metavar = 'string', help = 'The project description')
  optional_arguments.add_argument('--privacy_level', '-l', required = False, metavar = 'string', help = 'The projects privacy level. Default: private')

  # Post a ped file when creating the project or set the family name
  optional_arguments.add_argument('--ped_file', '-pf', required = False, metavar = 'string', help = 'A ped file to create samples')
  optional_arguments.add_argument('--family_name', '-f', required = False, metavar = 'string', help = 'The family name to apply to the project')

  # Information for creating a collection
  optional_arguments.add_argument('--is_collection', '-co', required = False, action = 'store_true', help = 'Set if this is to be a collection, not a project')
  optional_arguments.add_argument('--collection_projects', '-cp', required = False, metavar = 'string', help = 'If is_collection is set, a list of project ids to add to the collection can be set')

  # Set the project template
  optional_arguments.add_argument('--template_project_id', '-t', required = False, metavar = 'integer', help = 'Supply the id of a template project to apply this template on creation')

  # Set the attribute forms
  optional_arguments.add_argument('--attribute_forms', '-af', required = False, metavar = 'string', help = 'Comma separated list of attribute forms to associate with the project')

  return parser.parse_args()

if __name__ == "__main__":
  main()
