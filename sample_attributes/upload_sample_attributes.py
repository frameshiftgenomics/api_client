import os
import sys

from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Otherwise open this project ready for annotation upload
  try:
    project = api_mosaic.get_project(args.project_id)
  except Exception as e:
    fail('failed to open project. Error was: ' + str(e))

  # Get all the sample attributes in the project
  uids = []
  try:
    for attribute in project.get_sample_attributes():
      uids.append(attribute['uid'])
  except:
    fail('failed to get sample attributes for project')

  # Get the header line of thr tsv
  try:
    with open(args.tsv, 'r') as file:
      header = file.readline().rstrip().split('\t')

      # The header must begin with 'SAMPLE_NAME'
      if str(header[0]) != 'SAMPLE_NAME':
        fail('the tsv header must begin with SAMPLE_NAME')

      # The remaining fields must be sample attribute uids
      for uid in header[1:]:
        if uid not in uids:
          fail('unknown uid (' + str(uid) + ') in tsv header')

  except FileNotFoundError:
    fail('failed to open tsv file')

  # Disable notifications for successful uploads
  disable_successful_notifications = 'true' if args.disable_successful_notification else 'false'

  # Upload the sample attributes file
  try:
    project.post_upload_sample_attributes(args.tsv, disable_successful_notification = disable_successful_notifications)
  except Exception as e:
    fail('Failed to upload sample attributes. Error was: ' + str(e))

# Input options
def parse_command_line():
  parser, groups = base_parser()
  required_arguments = groups.required
  optional_arguments = groups.optional

  # The project id
  parser.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id to upload annotations to. Only necessary for private or custom annotations')

  # Additional arguments
  required_arguments.add_argument('--tsv', '-t', required = True, metavar = 'string', help = 'The annotation tsv file to upload')

  # Optional arguments
  optional_arguments.add_argument('--disable_successful_notification', '-n', required = False, action = 'store_false', help = 'Only send notifications if the upload fails. Default: true')

  return parser.parse_args()

if __name__ == "__main__":
  main()
