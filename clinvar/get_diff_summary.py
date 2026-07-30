import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Get the diff summary
  try:
    summary_by_project = {}
    for summary in api_mosaic.get_clinvar_diff_summary(args.annotation_version_id_a, args.annotation_version_id_b):
      project_id = summary['project_id']
      if project_id not in summary_by_project:
        summary_by_project[project_id] = [summary]
      else:
        summary_by_project[project_id].append(summary)

    # Print out the data
    for project_id in summary_by_project:
      print('Project:', project_id)
      for summary in summary_by_project[project_id]:
        print(summary)
  except Exception as e:
    fail('failed to get summary. Error was: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  required_arguments = groups.required

  # The ClinVar versions to diff
  required_arguments.add_argument('--annotation_version_id_a', '-va', required = True, metavar = 'integer', help = 'The old ClinVar annotation version id')
  required_arguments.add_argument('--annotation_version_id_b', '-vb', required = True, metavar = 'integer', help = 'The new ClinVar annotation version id')

  return parser.parse_args()

if __name__ == "__main__":
  main()
