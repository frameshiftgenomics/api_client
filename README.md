# api_client

```bash
cd api_client

python3 -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate

pip install requests

touch config.ini
```

The virtual environment keeps `requests` out of your system Python. It must be
active (`source .venv/bin/activate`) in each new shell before running any of the
scripts; use `deactivate` to leave it.

If you would rather not use one, `pip3 install requests` on its own is enough —
`requests` is the only dependency.

### config.ini

Generate an API token in the Mosaic UI. Update host and project ids accordingly.

```
[Configuration]
token = XXX
host = http://localhost:3000/api/v1

[Project ids]
annotations_grch37 = 1
annotations_grch38 = 2
```
