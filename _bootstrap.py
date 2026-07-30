"""
Shared start up code for the scripts in the api_client topic directories.

Every script repeats the same preamble: work out where the api client lives, put it
on the path, import mosaic, then open the Mosaic endpoints. This module holds that
preamble in one place. A script only needs to put the api_client directory onto the
path, which it can work out from its own location:

    import os
    import sys

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    from _bootstrap import base_parser, init, warning, fail

    def main():
      args = parse_command_line()
      api_mosaic = init(args)

base_parser() returns a parser holding the arguments that every script takes
(--client_config and --api_client), together with the standard argument groups. A
script adds its own arguments to those groups and parses:

    def parse_command_line():
      parser, groups = base_parser()
      groups.project.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id')
      groups.display.add_argument('--ids_only', '-io', required = False, action = 'store_true', help = 'Only output the ids')

      return parser.parse_args()

The groups are api, project, required, optional and display, carrying the same titles
the scripts have always used, so the help text of an already grouped script does not
change. A script needing a group of its own adds it to the returned parser:

      review_arguments = parser.add_argument_group('ClinVar Review Sets')

Two things to be careful of, since the api_client directory goes on the front of the
path for all of these scripts: do not add an __init__.py to a topic directory, and do
not add a file to the api_client directory whose name shadows a module from the
standard library. Either would break every script at once.

Note that unlike the preamble it replaces, this module locates the api client from
the position of the script rather than by splitting its path on the string
'api_client', so the directory no longer has to carry that name.
"""

import argparse
import os
import sys

from types import SimpleNamespace

# If the script fails, provide an error message and exit, alternatively provide a warning
def warning(message):
  print('WARNING: ', message, sep = '')

def fail(message):
  print('ERROR: ', message, sep = '')
  exit(1)

# Build a parser holding the arguments and groups common to all scripts. The parser is
# returned unparsed so that the calling script can add its own arguments
def base_parser():
  parser = argparse.ArgumentParser(description='Process the command line arguments')

  # The groups are created in the order they should appear in the help text
  groups = SimpleNamespace(
    api = parser.add_argument_group('API Arguments'),
    project = parser.add_argument_group('Project Arguments'),
    required = parser.add_argument_group('Required Arguments'),
    optional = parser.add_argument_group('Optional Arguments'),
    display = parser.add_argument_group('Display Information')
  )

  # Define the location of the api_client and the ini config file
  groups.api.add_argument('--client_config', '-c', required = True, metavar = 'string', help = 'The ini config file for Mosaic')
  groups.api.add_argument('--api_client', '-a', required = False, metavar = 'string', help = 'The api_client directory')

  return parser, groups

# Import the api client and open the Mosaic endpoints described by the config file
def init(args):

  # The script has already put its own api_client directory on the path. Only look
  # elsewhere if a different one was asked for
  if args.api_client:
    sys.path.insert(0, args.api_client)

  # Only an ImportError means the api client could not be found. Anything else (a broken
  # install of requests, for example) is a real error and should not be reported as a
  # missing api client
  try:
    from mosaic import Mosaic
  except ImportError as e:
    fail('Cannot find mosaic. Please set the --api_client / -a argument. Error was: ' + str(e))

  if not os.path.exists(args.client_config):
    fail('The config file does not exist: ' + str(args.client_config))

  try:
    api_mosaic = Mosaic(config_file = args.client_config)
  except Exception as e:
    fail('Failed to open the Mosaic api client. Error was: ' + str(e))

  return api_mosaic
