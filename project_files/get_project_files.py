import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # Get all project files
  for project_file in project.get_project_files():
    if args.verbose:
      print(project_file['name'])
      print('  id: ', project_file['id'], sep = '')
      print('  nickname: ', project_file['nickname'], sep = '')
      print('  type: ', project_file['type'], sep = '')
      print('  endpoint_url: ', project_file['endpoint_url'], sep = '')
      print('  experiment_ids: ', project_file['experiment_ids'], sep = '')
      print('  library_type: ', project_file['library_type'], sep = '')
      print('  reference: ', project_file['reference'], sep = '')
      print('  s3_bucket_id: ', project_file['s3_bucket_id'], sep = '')
      print('  s3_bucket_name: ', project_file['s3_bucket_name'], sep = '')
      print('  uri: ', project_file['uri'], sep = '')
    else:
      print(project_file['name'], ': ', project_file['id'], sep = '')

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # The project id
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id')

  # Verbose output
  parser.add_argument('--verbose', '-v', required = False, action = 'store_true', help = 'If set, provide a verbose output')

  return parser.parse_args()

if __name__ == "__main__":
  main()
