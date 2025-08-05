import os
import argparse

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
  api_store  = Store(config_file = args.client_config)
  api_mosaic = Mosaic(config_file = args.client_config)

  # Get the project ids of the GRCh37 and GRCh38 annotations
  grch37_annotations_project_id = api_mosaic._store.get('Project ids', 'annotations_grch37')
  grch38_annotations_project_id = api_mosaic._store.get('Project ids', 'annotations_grch38')

  # Get the uids of all annotations that originate in these projects
  available_annotations = {}
  grch37_project = api_mosaic.get_project(grch37_annotations_project_id)
  for annotation in grch37_project.get_variant_annotations():
    available_annotations[annotation['uid']] = annotation['original_project_id']

  grch38_annotations = {}
  grch38_project = api_mosaic.get_project(grch38_annotations_project_id)
  for annotation in grch38_project.get_variant_annotations():
    available_annotations[annotation['uid']] = annotation['original_project_id']
  
  # Get the uids of all the annotations in the tsv and determine their original project id
  upload_project_id = None
  user_defined_project = False
  user_project_uids = []
  try:
    with open(args.tsv) as f:
      for line in f.readlines():
        fields = line.rstrip().split('\t')

        # Loop over the annotation uids. The first 5 fields are coordinate information
        for uid in fields[5:]:
          if uid in available_annotations:

            # If this is the first uid in the tsv, set the upload_project_id to the original project id for this annotation
            if not upload_project_id:
              upload_project_id = available_annotations[uid]

            # Otherwise, check that this uid is for an annotation with the same original project id. The tsv file must
            # contain annotations being uploaded to the same project
            else:
              if int(available_annotations[uid]) != int(upload_project_id):
                fail('All annotation uids in the tsv must have the same original project id')

          # Private or custom annotations will not be in the globals projects. In this case, the user will need to supply the
          # project id to upload annotations to
          else:

            # If no project id is set, fail
            if not args.project_id:
              fail('Annotation with uid ' + str(uid) + ' is not from the GRCh37 or GRCh38 annotation projects. Please supply the project id (-p) to upload annotations to')

            # Otherwise check that the annotation is in the specified project
            else:

              # If this is the first annotation, set the upload_project_id to the id provided by the user
              if not upload_project_id:
                upload_project_id = args.project_id
                user_defined_project = True

              # Otherwise, check there are not annotations for multiple projects
              else:
                if int(args.project_id) != int(upload_project_id):
                  fail('All annotation uids in the tsv must have the same original project id')

              # Store the uid as it will need to be checked that it exists in the user defined project
              user_project_uids.append(uid)
        break
  except Exception as e:
    fail('Failed to open tsv file. Check the file is valid. Error was: ' + str(e))

  # If there is no upload_project_id, it is unknown which project to upload to
  if not upload_project_id:
    fail('Unable to determine which project to upload annotations to')

  # Otherwise open this project ready for annotation upload
  project = api_mosaic.get_project(upload_project_id)

  # If the annotations are being uploaded to a user defined project, ensure the annotations exist
  if user_defined_project:
    existing_uids = {}

    # Get all the annotations in the project
    for annotation in project.get_variant_annotations():
      existing_uids[annotation['uid']] = {'id': annotation['id'], 'versions': annotation['annotation_versions']}

    # Check all the required annotations exist. Note that the annotation uid may contain the version id. If
    # this is the case, also check that the version exists
    for file_uid in user_project_uids:
      uid = file_uid
      version = None
      if '@' in file_uid:
        uid = uid.split('@')[0]
        version = file_uid.split('@')[1]
      if uid not in existing_uids:
        fail('Annotation with uid ' + str(uid) + ' does not exist in the project specified with -p')

      # If there is a defined version, check that the version exists
      has_version = False
      if version:
        for version_info in existing_uids[uid]['versions']:
          if str(version) == str(version_info['version']):
            has_version = True
            break
      if not has_version:
        fail('Annotation with uid ' + str(uid) + ' does not have a version with the name ' + str(version))

  # Upload the variant annotations
  allow_deletion = 'true' if args.allow_deletion else 'false'
  disable_successful_notification = 'true' if args.disable_successful_notification else 'false'
  try:
    data = project.post_annotation_file(args.tsv, allow_deletion = allow_deletion, disable_successful_notification = disable_successful_notification)
    print(data['message'], '. Annotation upload job id: ', data['redis_job_id'], ', file: ', args.tsv, sep = '')
  except Exception as e:
    fail('Failed to upload annotations. Error was: ' + str(e))

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

  # The project id
  parser.add_argument('--project_id', '-p', required = False, metavar = 'integer', help = 'The Mosaic project id to upload annotations to. Only necessary for private or custom annotations')

  # Additional arguments
  required_arguments.add_argument('--tsv', '-t', required = True, metavar = 'string', help = 'The annotation tsv file to upload')
  optional_arguments.add_argument('--allow_deletion', '-d', required = False, action = 'store_true', help = 'If tsv file contains blank annotation, overwrite the existing value in the database will null. Default: false')
  optional_arguments.add_argument('--disable_successful_notification', '-n', required = False, action = 'store_false', help = 'Only send notifications if the upload fails. Default: true')

  return parser.parse_args()

# If the script fails, provide an error message and exit
def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

if __name__ == "__main__":
  main()
