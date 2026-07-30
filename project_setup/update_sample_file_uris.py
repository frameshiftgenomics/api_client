import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parseCommandLine()

  # Ensure the new uri terminates with a '/'
  if not args.uri.endswith('/'): args.uri += '/'

  api_mosaic = init(args)

  # Open an api client project object for the defined project
  project = api_mosaic.get_project(args.project_id)

  # Loop over all of the project files
  print('Project files:')
  for project_file in project.get_project_files():
    updated_uri = args.uri + project_file['name']
    print('  ', project_file['name'], sep = '')
    print('    ', project_file['uri'], ' > ', updated_uri, sep = '')
    success = project.put_project_file(project_file['id'], uri=updated_uri)

  # Loop over all of the samples in the project
  print()
  print('Sample files:')
  for sample in project.get_samples():
    print('  Sample ', sample['name'], ' (', sample['id'], ')', sep = '')

    # Get all of the sample files for each sample
    for sample_file in project.get_sample_files(sample['id']):
      updated_uri = args.uri + sample_file['name']
      print('    ', sample_file['uri'], ' > ', updated_uri, sep = '')
      success = project.put_sample_file(sample['id'], sample_file['id'], name=sample_file['name'], reference=sample_file['reference'], file_type=sample_file['type'], uri=updated_uri)

# Input options
def parseCommandLine():
  parser, _ = base_parser()

  # The project id to which the filter is to be added is required
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload attributes to')

  # The new uri path
  parser.add_argument('--uri', '-u', required = True, metavar = 'string', help = 'The path to update the file uris with')

  return parser.parse_args()

if __name__ == "__main__":
  main()
