import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():
  global api_mosaic
  global allowed_references
  global system_projects

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Check that the requested activity type is valid
  ### REPLACE WHEN ENDPOINT IS AVAILABLE TO GET VALUES
  allowed_activity_types = {'comment_posted': 1,
                            'conversation_posted': 2,
                            'sample_added': 3,
                            'attribute_added': 4,
                            'variants_added': 5,
                            'user_added': 6,
                            'expression_data_added': 7,
                            'variant_annotation_added': 8,
                            'gene_annotation_added': 9,
                            'analysis_published': 10,
                            'variant_set_published': 11,
                            'gene_set_published': 12,
                            'project_attribute_updated': 13,
                            'project_attribute_added': 14,
                            'collection_projects_added': 15,
                            'collection_projects_removed': 16,
                            'sample_set_published': 17,
                            'user_removed': 18,
                            'file_downloaded': 19,
                            'project_created': 20,
                            'project_deleted': 21,
                            'experiment_added': 22,
                            'job_submitted': 23,
                            'task_completed': 34,
                            'project_archived': 41,
                            'project_unarchive_requested': 42}
  if args.activity_type:
    if args.activity_type not in allowed_activity_types:
      fail('unknown activity type. Must be one of the following: ' + ', '.join(allowed_activity_types))

  # Open a project
  try:
    project = api_mosaic.get_project(args.project_id)
  except Exception as e:
    fail('failed to open project. Error was: ' + str(e))

  # Get the activities
  try:
    for activity in project.get_activities(from_date = args.from_date, to_date = args.to_date):
      is_display = True
      if args.activity_type:
        if args.activity_type != activity['type']:
          is_display = False

      # Display the requested activities
      if is_display:
        if args.display_raw_information:
          pprint(activity)
        elif args.display_activity:
          print(activity['id'], ': ', activity['type'], ', ', activity['message'], sep = '')
        elif args.output_ids_only:
          print(activity['id'])

        # Default output
        else:
          print(activity['id'], ': ', activity['type'], sep = '')
  except Exception as e:
    fail('failed to get activities. Error was: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  project_arguments = groups.project
  optional_arguments = groups.optional
  display_arguments = groups.display

  # Limit search to specific projects
  project_arguments.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id')

  # Additional filters
  optional_arguments.add_argument('--activity_type', '-t', required = False, metavar = 'string', help = 'Only display avtivities of this type')
  optional_arguments.add_argument('--from_date', '-fd', required = False, metavar = 'string', help = 'Only output activities after this date')
  optional_arguments.add_argument('--to_date', '-td', required = False, metavar = 'string', help = 'Only output activities before this date')

  # Display arguments
  display_arguments.add_argument('--output_ids_only', '-io', required = False, action = 'store_true', help = 'Only output the activity ids')
  display_arguments.add_argument('--display_activity', '-da', required = False, action = 'store_true', help = 'Only show the activity taht was taken')
  display_arguments.add_argument('--display_raw_information', '-dr', required = False, action = 'store_true', help = 'Show the full, raw activity information')

  return parser.parse_args()

api_mosaic = None

if __name__ == "__main__":
  main()
