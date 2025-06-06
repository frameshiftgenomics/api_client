import os
import argparse

from datetime import datetime
from pprint import pprint
from sys import path

def main():

  # Parse the command line
  args = parse_command_line()

  # If the api_client path was not specified, get it from the script path
  if not args.api_client:
    try:
      args.api_client = os.path.dirname(os.path.realpath(__file__)).split('api_client')[0] + str('api_client')
    except:
      fail('Could not get the api_client path from the command. Please specify using --api_client / -a')

  # Import the api client
  path.append(args.api_client)
  try:
    from mosaic import Mosaic, Project, Store
  except:
    fail('Cannot find mosaic. Please set the --api_client / -a argument')
  api_store = Store(config_file = args.client_config)
  api_mosaic = Mosaic(config_file = args.client_config)

  # Get the project settings
  job_statuses = args.status if args.status else None
  per_status_start = args.per_status_start if args.per_status_start else None
  per_status_end = args.per_status_end if args.per_status_end else None
  i = 1
  for job in api_mosaic.get_queue_status(per_status_start = per_status_start, per_status_end = per_status_end)['jobs']:

    # If only jobs of a particular status are to be output, check if the job has this status and only
    # output if it does
    if args.status:
      if str(args.status) == str(job['status']):
        print_job_info(job)

    # Otherwise output all jobs
    else:
      print_job_info(job)

    # Incrememnt the number of jobs and end if the top N have been seen
    i += 1
    if args.show_top_n:
      if int(i) > int(args.show_top_n):
        break

# Input options
def parse_command_line():
  parser = argparse.ArgumentParser(description='Process the command line arguments')
  api_arguments = parser.add_argument_group('API Arguments')
  project_arguments = parser.add_argument_group('Project Arguments')
  required_arguments = parser.add_argument_group('Required Arguments')
  optional_arguments = parser.add_argument_group('Optional Arguments')
  display_arguments = parser.add_argument_group('Display Information')

  # Define the location of the api_client and the ini config file
  api_arguments.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  api_arguments.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

  # Optional arguments
  optional_arguments.add_argument('--status', '-s', required = False, metavar = 'string', help = 'Only show jobs with this status. Options are: waiting, active, failed, completed')
  optional_arguments.add_argument('--per_status_start', '-t', required = False, metavar = 'integer', help = 'The start value of the job range to return')
  optional_arguments.add_argument('--per_status_end', '-e', required = False, metavar = 'integer', help = 'The end value of the job range to return')

  # The number of jobs to show
  display_arguments.add_argument('--show_top_n', '-n', required = False, metavar = 'integer', help = 'Show the top N jobs in the queue')

  return parser.parse_args()

# Print information about the job
def print_job_info(job):
  if 'file' in job:
    if 'job_type' in job:
      print(job['redis_job_id'], ', id: ', job['id'], ', status: ', job['status'], ', type: ', job['job_type'], ', file: ', job['file'], ', submitted at: ', datetime.fromtimestamp(job['timestamp'] / 1000), sep = '')
    else:
      print(job['redis_job_id'], ', id: ', job['id'], ', status: ', job['status'], ', file: ', job['file'], ', submitted at: ', datetime.fromtimestamp(job['timestamp'] / 1000), sep = '')
  else:
    print(job['redis_job_id'], ', id: ', job['id'], ', status: ', job['status'], ', type: ', job['job_type'], ', submitted at: ', datetime.fromtimestamp(job['timestamp'] / 1000), sep = '')

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
