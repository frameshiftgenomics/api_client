import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Post the s3 bucket user
  endpoint_url = args.endpoint_url if args.endpoint_url else None
  data = api_mosaic.post_s3_bucket_user(bucket_name = args.bucket_name, access_key_id = args.access_key_id, secret_access_key = args.secret_access_key, endpoint_url = endpoint_url)

# Input options
def parse_command_line():
  parser, _ = base_parser()

  # Required arguments
  parser.add_argument('--bucket_name', '-b', required = True, metavar = 'string', help = 'Resource identifier for the S3 Bucket to access')
  parser.add_argument('--secret_access_key', '-s', required = True, metavar = 'string', help = 'The Secret Access Key for the IAM User')
  parser.add_argument('--access_key_id', '-k', required = True, metavar = 'string', help = 'The Access Key ID for the IAM User')

  # Optional arguments
  parser.add_argument('--endpoint_url', '-u', required = False, metavar = 'string', help = 'The endpoint URL if using S3 Compatible Object Storage. The URL must end with a "/"')

  return parser.parse_args()

if __name__ == "__main__":
  main()
