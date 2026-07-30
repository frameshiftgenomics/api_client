import os
import sys

from datetime import datetime
from pprint import pprint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def main():

  # Parse the command line
  args = parse_command_line()

  api_mosaic = init(args)

  # Get the project settings
  job_statuses = args.status if args.status else None
  per_status_start = args.per_status_start if args.per_status_start else None
  per_status_end = args.per_status_end if args.per_status_end else None

  # If the number of jobs requested is greater than per_status_end, update per_status_end to the number of jobs to return.
  # If per_status_end is not set, it will default to 49, so if the requested number of jobs is larger than this also
  # update per_status_end
  if not per_status_end:
    if args.show_top_n:
      per_status_end = args.show_top_n
  else:
    if args.show_top_n:
      if int(args.show_top_n) > int(per_status_end):
        per_status_end = args.show_top_n

  if args.show_top_n:
    per_status_end = args.show_top_n

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
  parser, groups = base_parser()
  optional_arguments = groups.optional
  display_arguments = groups.display

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

if __name__ == "__main__":
  main()
