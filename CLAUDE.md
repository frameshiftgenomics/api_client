# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Python client for the Frameshift **Mosaic** REST API, plus ~200 standalone CLI scripts that use it.

Two layers:

1. `mosaic.py` (~2300 lines) — the entire client library. One file, three classes.
2. Topic directories (`projects/`, `samples/`, `variant_annotations/`, `views/`, …) — thin, single-purpose CLI wrappers around client methods. Directory names mirror Mosaic API resource groups; file names mirror the HTTP verb + route (`projects/post_project.py`, `views/put_update_view.py`).

There is no build, no test suite, no linter, and no packaging. Scripts are run directly.

## Setup

```bash
pip3 install requests          # only hard dependency
```

A `.venv/` (Python 3.13) exists locally. `*.ini` is gitignored — config files hold live API tokens and must never be committed.

`config.ini`:

```
[Configuration]
token = <generated in the Mosaic UI>
host = http://localhost:3000/api/v1

[Project ids]
annotations_grch37 = 1
annotations_grch38 = 2
```

## Running things

Every script takes the same two API arguments:

```bash
python3 projects/get_projects.py -c config.ini
python3 project_attributes/put_project_attributes.py -c config.ini -p 123 -i 456 --name "New name"
```

- `--client_config` / `-c` (**required**) — path to the ini file. A few older scripts call this `--config` / `-c`.
- `--api_client` / `-a` (optional) — path to this repo. Scripts still on the legacy preamble derive it by splitting their own realpath on the literal string `api_client`, so **for those the checkout directory must be named `api_client`** or `-a` becomes mandatory. Scripts migrated to `_bootstrap.py` locate the repo from their own position instead, making the flag vestigial for them.
- `--project_id` / `-p` — required by any script that operates on a project.

Interactive/interpreter use:

```python
from mosaic import Mosaic
api_mosaic = Mosaic(config_file='config.ini')
project = api_mosaic.get_project(123)
for attribute in project.get_project_attributes():
    print(attribute['name'])
```

`mosaic.py` also has a `python-fire` entrypoint (`python mosaic.py project --project-id=1 <method>`), but `fire` is not installed in `.venv` and this path is rarely used.

## Architecture of `mosaic.py`

**`Store`** — thin `configparser` wrapper over the ini file; `get`/`set` (set writes back to disk).

**`Mosaic`** — auth headers, HTTP verbs, and all **non-project-scoped** routes (`get_projects`, `get_hpo_terms`, `get_user_by_email`, `post_policies`, whitelist/super-admin, role types, data resources…).

- `_http_request` is the single choke point: coerces list query params to `key[]`, `json.dumps` bodies to avoid form encoding, handles multipart when `file_upload` is passed (clears `Content-Type` so `requests` sets the boundary), and re-raises non-2xx as `HTTPError` carrying the server's `message` field.
- Every request is recorded as a replayable `curl` string in `_request_history` (`request_history()`).
- `get_paged_route_iter(resource, params=...)` — generator that walks `page`/`limit` until `count` is satisfied. **Any list endpoint should be exposed with `yield from get_paged_route_iter(...)`, not a bare `get()`**; ~17 methods already do this, and callers iterate rather than index.

**`Project`** — everything under `projects/{id}`. Holds a reference to its backing `Mosaic` (`self._mosaic`) and a path prefix (`self._path = f"projects/{self.id}"`); all methods build routes from that prefix. Constructed via `api_mosaic.get_project(project_id)`, which fetches the project first so `.name` and `.data` are populated.

Collections are just projects with `is_collection` true and a `collection_project_ids` list — scripts that must work on both typically fan out over that list (see `project_setup/set_project_defaults.py`).

### Adding an endpoint

Add a method to `Mosaic` or `Project` (whichever the route is scoped to), placed under the existing `""" SECTION """` comment banner for that resource group, alphabetically within the section. House style for the method body:

```python
def put_something(self, thing_id, *, name=None, description=None):
    data = { }
    if name:
        data['name'] = name
    if description:
        data['description'] = description

    return self._mosaic.put(f'{self._path}/things/{thing_id}', data=data)
```

Required values are positional; everything optional is keyword-only and omitted from the payload when falsy.

## Script conventions

Two start-up patterns coexist. **New and migrated scripts use `_bootstrap.py`; the other ~203 still carry the old copied preamble.** Match whichever the file you are editing already uses — do not migrate a script as a side effect of an unrelated change.

### `_bootstrap.py` (the pattern to use for new scripts)

```python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from _bootstrap import base_parser, init, fail

def parse_command_line():
  parser, groups = base_parser()
  groups.project.add_argument('--project_id', '-p', required = True, metavar = 'integer', help = 'The Mosaic project id')
  return parser.parse_args()

def main():
  args = parse_command_line()
  api_mosaic = init(args)
```

- `base_parser()` returns `(parser, groups)`. `groups` is a `SimpleNamespace` with `.api .project .required .optional .display`, pre-titled to match the legacy group names, and already carrying `--client_config` and `--api_client`. A script needing its own group adds it to the returned `parser`.
- `init(args)` returns **only** `api_mosaic`. It does not return a `Store` — the old preamble built one in 203 of 205 scripts and none used it. Read config via `api_mosaic.get_config(section, key)`.
- `fail`/`warning` come from `_bootstrap`; don't redefine them.
- Because the repo root goes on the front of `sys.path` for every script, never add an `__init__.py` to a topic directory, and never add a root-level file whose name shadows a stdlib module.
- `project_attributes/get_project_attributes.py` is the reference migration.

### The legacy preamble (still in ~203 scripts)

- Fixed opening boilerplate: `parse_command_line()`, derive `args.api_client` by splitting the script path on the string `api_client`, `path.append`, `from mosaic import Mosaic, Project, Store`, then build `api_store` / `api_mosaic` — all inside `main()`, each step wrapped in `try/except` that calls `fail()`. (`Project` is imported by every script and instantiated by none; `api_store` is likewise unused.)
- Each script defines its own module-level `fail(message)` (prints `ERROR: …`, `exit(1)`) and sometimes `warning(message)`. `mosaic.py` has its own copies.

### Both patterns

- **2-space indentation** in scripts and `_bootstrap.py`; **4-space** in `mosaic.py`.
- `argparse` uses named groups (`API Arguments`, `Project Arguments`, `Required Arguments`, `Optional Arguments`, `Display Information`) and spaces around `=` in kwargs (`required = False`). 81 of the 205 scripts use no groups at all.
- Output goes to stdout via `print`/`pprint`; most scripts offer `--raw_output`/`-ro` or `--display_all`/`-da` for a full dump. Scripts do not return values, do not prompt for confirmation (including the `delete_all_*` ones), and validate enum-ish inputs against a local `allowed_*` list before calling the API.
- `--ids_only` / `-io` is the convention for machine-readable output meant to be piped into another script.
- 9 scripts name the config flag `--config` rather than `--client_config`; `init()` reads `args.client_config`, so those need renaming when migrated.

`project_attributes/get_project_attributes_test.py` is the prototype that led to `_bootstrap.py`. It is a lossy subset of `get_project_attributes.py` (missing `--ids_only`, `--only_longitudinal`, `--in_data_groups`, `--list_data_groups`, `--find_single_predefined_value_with_comma`) and is a deletion candidate — prefer the reference migration as the example to copy.

## Other directories

- `project_setup/` — multi-step provisioning scripts driven by JSON config (`project_defaults_GRCh37.json`, `project_defaults_GRCh38.json`, `annotations.json`) that map attribute UIDs to sample-table columns, charts, and variant filters.
- `custom_scripts/` and `maintenance_scripts/` — one-off reporting and data-cleanup jobs (UDN/NIH-specific), not general API wrappers.
- `super_admin/` — routes requiring elevated tokens.
