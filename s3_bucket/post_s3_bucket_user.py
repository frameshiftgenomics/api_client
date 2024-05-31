import argparse
import json
import os

from sys import path

def main():

  # Parse the command line
  args = parseCommandLine()

  # Import the api client
  path.append(args.api_client)
  from mosaic import Mosaic, Project, Store
  apiStore  = Store(config_file = args.client_config)
  apiMosaic = Mosaic(config_file = args.client_config)

  # Post the s3 bucket user
  endpoint_url = args.endpoint_url if args.endpoint_url else None
  data = apiMosaic.post_s3_bucket_user(bucket_name = args.bucket_name, access_key_id = args.access_key_id, secret_access_key = args.secret_access_key, endpoint_url = endpoint_url)

# Input options
def parseCommandLine():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # Define the location of the api_client and the ini config file
  parser.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  parser.add_argument('--api_client', '-a', required = True, metavar = 'string', help = 'The api_client directory')

  # Required arguments
  parser.add_argument('--bucket_name', '-b', required = True, metavar = 'string', help = 'Resource identifier for the S3 Bucket to access')
  parser.add_argument('--secret_access_key', '-s', required = True, metavar = 'string', help = 'The Secret Access Key for the IAM User')
  parser.add_argument('--access_key_id', '-k', required = True, metavar = 'string', help = 'The Access Key ID for the IAM User')

  # Optional arguments
  parser.add_argument('--endpoint_url', '-u', required = False, metavar = 'string', help = 'The endpoint URL if using S3 Compatible Object Storage. The URL must end with a "/"')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print(message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
