import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from project_setup import set_variant_filters

# Replace every variant filter in a project with the set described by the filter json. This is
# project_setup/set_variant_filters.py with the deletion of the existing filters always on, so
# the implementation is shared with that script rather than held as a second copy here.
#
# The copy this script used to carry had never run: it read a filter json it never asked for on
# the command line, called four helper functions it did not define, and built its annotation
# records in the shape set_variant_filters.py abandoned when annotation versions arrived. Sharing
# the implementation is what stops that drift happening again.
def main():
  if not any(argument in sys.argv for argument in ('--delete_existing_filters', '-d')):
    sys.argv.append('--delete_existing_filters')

  set_variant_filters.main()

if __name__ == "__main__":
  main()
