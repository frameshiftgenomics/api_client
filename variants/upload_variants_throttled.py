import os
import sys
import time

from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, warning, fail

# Upload variants from many vcf files, only submitting a new upload when the number of the user's
# jobs still waiting or running in the Mosaic queue is below a threshold. Each upload copies its vcf
# into Mosaic's temp space until the job finishes, so queueing thousands at once fills it up.
#
# The input file is tab separated, one upload per line:
#
#   vcf_path <TAB> project_id [<TAB> sample_map_path]
#
# Blank lines and lines starting with '#' are ignored. Each upload is recorded in the log file as it is
# submitted, and uploads already recorded as submitted are skipped, so an interrupted run can simply be
# restarted with the same arguments. Uploads that failed to submit are retried on a rerun.

# The job statuses for which the uploaded file is still held in temp space
pending_statuses = ['waiting', 'active', 'delayed']

# The jobs route returns at most this many jobs per status (the range per_status_start - per_status_end is
# capped at 200, inclusive)
max_jobs_per_status = 201

def main():

  # Parse the command line
  args = parse_command_line()

  # Check the inputs before starting, so a bad line does not stop a run part way through
  allowed_methods = ['allele', 'no-validation', 'position', 'raw', 'sv-no-validation']
  if args.method not in allowed_methods:
    fail('--method must be one of: ' + ', '.join(allowed_methods))
  if args.max_jobs < 1 or args.max_jobs >= max_jobs_per_status:
    fail('--max_jobs must be between 1 and ' + str(max_jobs_per_status - 1))
  if args.wait < 1:
    fail('--wait must be at least 1 second')
  uploads = read_uploads(args.input)

  # Skip the uploads that a previous run already submitted
  submitted = read_submitted(args.log)
  to_upload = [upload for upload in uploads if (upload['vcf'], upload['project_id']) not in submitted]
  print('Uploads in input: ', len(uploads), ', already submitted: ', len(uploads) - len(to_upload), ', to submit: ', len(to_upload), sep = '')
  if not to_upload:
    return

  api_mosaic = init(args)
  notifications = 'false' if args.enable_notifications else 'true'

  # Project objects are cached, since many vcf files are likely to go to the same project
  projects = {}
  n_submitted = 0
  n_failed = 0
  with open(args.log, 'a') as log:
    for i, upload in enumerate(to_upload, start = 1):

      # Wait until there is room in the queue
      wait_for_queue(api_mosaic, args.max_jobs, args.wait)

      prefix = '[' + str(i) + '/' + str(len(to_upload)) + '] '
      try:
        if upload['project_id'] not in projects:
          projects[upload['project_id']] = api_mosaic.get_project(upload['project_id'])
        project = projects[upload['project_id']]
        data = project.post_variant_file(upload['vcf'], upload_type = args.method, disable_successful_notification = notifications, sample_map = upload['sample_map'])
        job_id = data['redis_job_id'] if data and 'redis_job_id' in data else ''
        write_log(log, upload, 'submitted', job_id)
        print(prefix, 'Submitted ', upload['vcf'], ' to project ', upload['project_id'], ', job: ', job_id, sep = '')
        n_submitted += 1
      except Exception as e:
        error = ' '.join(str(e).split())
        write_log(log, upload, 'failed', error)
        warning(prefix + 'Failed to submit ' + upload['vcf'] + ' to project ' + upload['project_id'] + ': ' + error)
        n_failed += 1

  print('Finished. Submitted: ', n_submitted, ', failed to submit: ', n_failed, ', log: ', args.log, sep = '')
  if n_failed > 0:
    print('Rerun with the same arguments to retry the failed uploads')

# Input options
def parse_command_line():
  parser, groups = base_parser()
  required_arguments = groups.required
  optional_arguments = groups.optional

  required_arguments.add_argument('--input', '-i', required = True, metavar = 'string', help = 'Tab separated file of uploads: vcf path, project id and, optionally, a sample map path')
  required_arguments.add_argument('--method', '-m', required = True, metavar = 'string', help = 'The variant upload method: "allele, no-validation, position, raw, sv-no-validation"')
  optional_arguments.add_argument('--max_jobs', '-j', required = False, type = int, default = 5, metavar = 'integer', help = 'Only submit an upload when fewer than this many of your jobs are waiting, active or delayed. Default: 5')
  optional_arguments.add_argument('--wait', '-w', required = False, type = int, default = 60, metavar = 'integer', help = 'Seconds to wait before checking the queue again when it is full. Default: 60')
  optional_arguments.add_argument('--log', '-l', required = False, default = 'upload_variants_throttled.log', metavar = 'string', help = 'Log of submitted uploads, used to resume an interrupted run. Default: upload_variants_throttled.log')
  optional_arguments.add_argument('--enable_notifications', '-e', required = False, action = 'store_true', help = 'If set, notifications will be provided. Otherwise, notifications will only be provided for failures')

  return parser.parse_args()

# Read and check the list of uploads
def read_uploads(input_file):
  if not os.path.exists(input_file):
    fail('The input file does not exist: ' + str(input_file))

  uploads = []
  errors = []
  with open(input_file) as f:
    for line_number, line in enumerate(f, start = 1):
      line = line.rstrip('\n')
      if not line.strip() or line.startswith('#'):
        continue
      fields = [field.strip() for field in line.split('\t')]
      if len(fields) < 2 or len(fields) > 3:
        errors.append('line ' + str(line_number) + ': expected 2 or 3 tab separated columns')
        continue

      vcf = os.path.abspath(os.path.expanduser(fields[0]))
      project_id = fields[1]
      sample_map = os.path.abspath(os.path.expanduser(fields[2])) if len(fields) == 3 and fields[2] else None

      if not project_id.isdigit():
        errors.append('line ' + str(line_number) + ': project id is not an integer: ' + project_id)
      if not vcf.endswith('.vcf.gz') and not vcf.endswith('.bcf'):
        errors.append('line ' + str(line_number) + ': file must be a .vcf.gz or .bcf: ' + vcf)
      elif not os.path.exists(vcf):
        errors.append('line ' + str(line_number) + ': vcf file does not exist: ' + vcf)
      if sample_map and not os.path.exists(sample_map):
        errors.append('line ' + str(line_number) + ': sample map does not exist: ' + sample_map)

      uploads.append({'vcf': vcf, 'project_id': project_id, 'sample_map': sample_map})

  if errors:
    fail('Problems with the input file ' + input_file + ':\n  ' + '\n  '.join(errors))
  if not uploads:
    fail('The input file contains no uploads: ' + input_file)

  return uploads

# Read the (vcf, project id) pairs already submitted from the log file
def read_submitted(log_file):
  submitted = set()
  if os.path.exists(log_file):
    with open(log_file) as f:
      for line in f:
        fields = line.rstrip('\n').split('\t')
        if len(fields) >= 4 and fields[3] == 'submitted':
          submitted.add((fields[1], fields[2]))

  return submitted

# Record the result of an upload, flushing so the log is current if the run is interrupted
def write_log(log, upload, status, detail):
  print(datetime.now().isoformat(timespec = 'seconds'), upload['vcf'], upload['project_id'], status, detail, sep = '\t', file = log)
  log.flush()

# Count the user's jobs, across all queues, whose files are still in temp space
def get_pending_job_count(api_mosaic):
  data = api_mosaic.get('jobs', params = {'job_statuses': pending_statuses, 'per_status_start': 0, 'per_status_end': max_jobs_per_status - 1})
  return data['count']

# Block until fewer than max_jobs of the user's jobs are pending. If the queue cannot be read, keep waiting
# rather than submitting blind
def wait_for_queue(api_mosaic, max_jobs, wait):
  waiting_reported = False
  while True:
    try:
      count = get_pending_job_count(api_mosaic)
      if count < max_jobs:
        return
      if not waiting_reported:
        print(datetime.now().strftime('%H:%M:%S'), ' Queue has ', count, ' pending jobs (limit ', max_jobs, '), waiting...', sep = '')
        waiting_reported = True
    except Exception as e:
      warning('Could not read the queue status, retrying in ' + str(wait) + 's: ' + ' '.join(str(e).split()))
    time.sleep(wait)

if __name__ == "__main__":
  main()
