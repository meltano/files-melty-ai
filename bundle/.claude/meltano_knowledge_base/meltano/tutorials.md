# Tutorials

Step-by-step tutorials for building a custom extractor, and integrating Meltano with Jupyter, DataHub, and example/community projects.

## Create a Custom Extractor

Custom extractors source data from unconventional data sources (a custom database, a SaaS API) and present it in a form loadable into a target sink. "Custom" means the extractor isn't a native part of the tool.

Singer is the commonly used specification for implementing extractors (taps) and loaders (targets). A custom extractor built with Singer is a Singer tap written for your organization's needs. Meltano's EL features handle the Singer complexity of configuration, stream discovery, and state management, so taps/targets are best run as Meltano extractor/loader plugins.

### Prerequisites

1. Python 3 (https://www.python.org/downloads/)
2. `uv` (0.3.0+) for dependency management — a fast Python package manager
3. Cookiecutter, for installing the template repository

Install Python 3 via `uv`:
```bash
uv python install 3.13
```
Install Meltano and Cookiecutter:
```bash
uv tool install meltano
uv tool install cookiecutter
```

### 1. Create a project from the Cookiecutter template

```bash
cookiecutter https://github.com/meltano/sdk --directory="cookiecutter/tap-template"
```
You'll be prompted to configure the project — for a demo, use `jsonplaceholder` as the source name. The result is a new `tap-jsonplaceholder` directory with boilerplate tap code and a `meltano.yml` for testing. Template source: github.com/meltano/sdk (cookiecutter directory).

### 2. Install Python dependencies

```bash
cd tap-jsonplaceholder
uv sync
```

### 3. Configure the tap to consume data from the source

Set the API URL and streams to replicate. In `tap-jsonplaceholder/tap_jsonplaceholder/tap.py`:

```python
"""jsonplaceholder tap class."""

from typing import List

from singer_sdk import Tap, Stream

from singer_sdk import typing as th  # JSON schema typing helpers

from tap_jsonplaceholder.streams import jsonplaceholderStream, CommentsStream


STREAM_TYPES = [CommentsStream]


class Tapjsonplaceholder(Tap):
    """jsonplaceholder tap class."""

    name = "tap-jsonplaceholder"

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""

        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
```

In `tap-jsonplaceholder/tap_jsonplaceholder/streams.py`:

```python
"""Stream type classes for tap-jsonplaceholder."""

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_jsonplaceholder.client import jsonplaceholderStream


class CommentsStream(jsonplaceholderStream):
    primary_keys = ["id"]
    path = "/comments"
    name = "comments"
    schema = th.PropertiesList(
        th.Property("postId", th.IntegerType),
        th.Property("id", th.IntegerType),
        th.Property("name", th.StringType),
        th.Property("email", th.StringType),
        th.Property("body", th.StringType),
    ).to_dict()
```

`tap.py` defines the tap and available streams (`STREAM_TYPES`). `streams.py` configures the `comments` stream (path, extracted field properties). Also set `url_base` in `tap-jsonplaceholder/tap_jsonplaceholder/client.py`:

```python
class jsonplaceholderStream(RESTStream):
    """jsonplaceholder stream class."""

    # TODO: Set the API's base URL here:
    url_base = "https://jsonplaceholder.typicode.com"
```

### 4. Install and run the tap

```bash
meltano install
meltano add target-jsonl
meltano run tap-jsonplaceholder target-jsonl
head -n 5 output/comments.jsonl
```

Sample output line:
```json
{"postId": 1, "id": 1, "name": "id labore ex et quam laborum", "email": "Eliseo@gardner.biz", "body": "laudantium enim quasi est quidem magnam voluptate ipsam eos\ntempora quo necessitatibus\ndolor quam autem quasi\nreiciendis et nam sapiente accusantium"}
```

### Interacting with the plugin

```bash
meltano invoke tap-my-custom-source                    # run in isolation
meltano invoke tap-my-custom-source --discover          # see supported streams
meltano select --list --all                             # list all entities/attributes from the catalog
```

### Adding the custom extractor to a Meltano project

If starting fresh:
```bash
meltano init
cd meltano-demo
```

**Option 1 — `meltano add`:**
```bash
meltano add --custom tap-jsonplaceholder
```
You'll be prompted for the namespace URL (`tap-jsonplaceholder`) and `pip_url` — use `-e ../tap-jsonplaceholder` for a local project path. Accept the default executable name; capabilities/settings can be left blank initially.

Alternatively, create a plugin definition YAML file and add via `--from-ref`:
```yaml
# tap-jsonplaceholder.yml
name: tap-jsonplaceholder
namespace: tap_jsonplaceholder
pip_url: -e ../tap-jsonplaceholder
```
```bash
meltano add --from-ref tap-jsonplaceholder.yml tap-jsonplaceholder
```
The plugin name must be present in the YAML file for it to be a valid definition — supplying it as a command argument is a no-op in this case.

To update settings as the tap evolves (new/renamed/removed settings), maintain the YAML file and re-run with `--update`:
```bash
meltano add --update --from-ref tap-jsonplaceholder.yml tap-jsonplaceholder
```

Add a JSONL target and run:
```bash
meltano add target-jsonl
meltano run tap-jsonplaceholder target-jsonl
head -n 5 output/comments.jsonl
```

**Option 2 — edit `meltano.yml` directly:**
```yaml
plugins:
  extractors:
    - name: tap-my-custom-source
      namespace: tap_my_custom_source
      # Editable-mode local path install (https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs)
      pip_url: -e /path/to/tap-my-custom-source
      # Executable name — found in the tap's pyproject.toml CLI declaration
      executable: tap-my-custom-source
      capabilities:
        - state
        - catalog
        - discover
      config:
        username: me@example.com
        start_date: '2024-01-01'
      settings:
        - name: username
        - name: password
          sensitive: true
        - name: start_date
          value: '2010-01-01T00:00:00Z'
  loaders:
    - name: target-jsonl
      variant: andyh1203
      pip_url: target-jsonl
```

Appearance can be further customized via `label`, `logo_url`, `description`. After manually editing `meltano.yml`, rerun `meltano install`.

### Plugin settings

When defining settings for a custom extractor:

- **name** — the setting's identifier; determines how the value is passed to the underlying component. Nesting via `.` separator (`foo.a` → `{ foo: { a: VALUE } }`).
- **kind** (optional) — value type (e.g. `date_iso8601`). Defaults to `string`.
- **sensitive** (optional, default `false`) — whether the setting is sensitive (password, token, code).
- **value** (optional) — default value.

**Passing sensitive values:** don't store sensitive values directly in `meltano.yml`. Mark the setting `sensitive: true` and set the value via `meltano config set <plugin> password <value>`, or via the matching environment variable (e.g. `export TAP_MY_CUSTOM_SOURCE_PASSWORD=<value>`). Configuration precedence: environment variables > `config` section in the plugin > the setting's `value` default.

### Publishing to PyPI

If built with the SDK, use `uv publish`:

1. Create a PyPI account.
2. Set up publishing credentials — a Trusted Publisher (for GitHub Actions) or a PyPI API token.
3. `uv build` to build the package.
4. `uv publish` with `--trusted-publishing=automatic` or `--token=<token>`.

**Verify installation** (recommend `uv` to avoid dependency conflicts):
```bash
uvx --from git+https://github.com/myusername/tap-my-custom-source.git tap-my-custom-source --help
uvx tap-my-custom-source --help   # from PyPI, if published
```

**Make it discoverable:** once published to PyPI or tagged with a GitHub release, it can be added to Meltano Hub's plugin catalog for other users.

**Updates for production use:**
1. Create a GitHub release (e.g. `v1.0.0`).
2. Add `pip_url: git+https://github.com/myusername/tap-my-custom-source@v1.0.0` (or `pip_url: tap-my-custom-source` if published to PyPI).
3. Rerun `meltano install`.

**References:** SDK for Singer Taps and Targets (sdk.meltano.com), Singer Spec (hub.meltano.com/singer/spec).

---

## How to use DataHub with Meltano

DataHub is a metadata platform, integrated via Meltano's `datahub` utility plugin.

**Components needed:**
- A DataHub GMS (Generalized Metadata Service) — local or remote
- The DataHub CLI, used to ingest metadata into the GMS (installed via the utility)
- Meltano linking the components together
- One ingestion recipe per source (a dbt recipe ships with the utility)

**Running a local DataHub:** install DataHub, then run `datahub docker quickstart` to launch the docker-compose cluster (sample data ingestion isn't required). UI defaults to `http://localhost:9002/`; local GMS URL defaults to `http://localhost:8080`.

**Installing the utility:** first identify which DataHub modules (sources) you need — e.g. `s3`, `postgres`, `dbt`. Via CLI:
```bash
meltano add utility datahub[s3,postgres,dbt]
```
This populates `meltano.yml`:
```yaml
utilities:
  - name: datahub
    variant: datahub-project[s3,postgres,dbt]
    pip_url: acryl-datahub
    config:
      gms_host:
      gms_auth:
```

**Configuring the utility:** if DataHub's metadata service authentication (MSA) is off, only `gms_host` is needed:
```yaml
utilities:
  - name: datahub
    variant: datahub-project
    pip_url: acryl-datahub[s3,postgres,dbt]
    config:
      gms_host: http://localhost:8080
```
or `meltano config set datahub gms_host http://localhost:8080`. If MSA is on, also set `gms_auth`:
```yaml
config:
  gms_host: http://localhost/gms/api
  gms_auth: myToken
```
or `meltano config set datahub gms_auth myToken`.

**Setting recipes:** one recipe per source, written in YAML and stored as `*.dhub.yml` files. The utility ships a preconfigured dbt recipe (adapt the `platform` parameter):
```yaml
source:
  type: "dbt"
  config:
    manifest_path: ${MELTANO_PROJECT_ROOT}/.meltano/transformers/dbt/target/manifest.json
    catalog_path: ${MELTANO_PROJECT_ROOT}/.meltano/transformers/dbt/target/catalog.json
    sources_path: ${MELTANO_PROJECT_ROOT}/.meltano/transformers/dbt/target/sources.json
    # Change to the appropriate platform, e.g. bigquery, postgres, etc.
    target_platform: "CHANGE ME"
sink:
  type: datahub-rest
  config:
    server: ${DATAHUB_GMS_HOST}
    token: ${DATAHUB_GMS_TOKEN}
```
The dbt recipe lives in `${MELTANO_PROJECT_ROOT}/utilities/datahub/`, but recipes can be placed anywhere.

Sample S3 ingestion recipe:
```yaml
source:
  type: s3
  config:
    path_specs:
      -
        include: "s3://test/*.csv"
    aws_config:
      aws_access_key_id: XXX
      aws_secret_access_key: XXX
      aws_region: us-east-1
      aws_endpoint_url: http://host.docker.internal:5005 # mock, replace with yours
    env: "PROD"
    profiling:
      enabled: false
```

Sample PostgreSQL ingestion recipe:
```yaml
source:
  type: postgres
  config:
    host_port: host.docker.internal:5432
    database: demo
    username: admin
    password: password
```

**Running ingestion:**
```bash
meltano invoke datahub ingest -c YOURRECIPE.dhub.yaml
meltano invoke datahub ingest -c s3recipe.dhub.yaml
meltano invoke datahub ingest -c postgresrecipe.dhub.yaml

meltano invoke datahub :dbt-ingest   # dbt ingestion
```
For the dbt ingestion to work, `source freshness` and `docs generate` must have been run beforehand:
```bash
meltano invoke dbt-postgres:docs-generate
meltano invoke dbt-postgres:freshness
```

**More resources:** an example repository (github.com/sbalnojan/meltano-example-eltm) accompanies this guide; see also the file bundle and utility READMEs at github.com/z3z1ma/files-datahub.

---

## Example Meltano Projects

Community and production examples, grouped into three categories.

### 1. Running in production

- **Meltano Squared** (github.com/meltano/squared) — the project the Meltano team uses to manage their own Meltano instance. Runs on Kubernetes; uses multiple YAML files, environments, plugin inheritance, Great Expectations, SQLFluff, dbt, Airflow, and Superset.
- **GitLab Data Meltano** (gitlab.com/gitlab-data/gitlab-data-meltano) — the project GitLab uses to manage Meltano.

### 2. Simple example projects

Illustrate a solution to one problem.

- **Meltano & SQLFluff for dbt** (gitlab.com/rabidaudio/meltano-sqlfluff-example) — SQLFluff set up via Meltano as a dbt linter.
- **Data Stack 4 Fun & Nonprofits** (github.com/andrewcstewart/ds4fnp) — larger setup with a tutorial series: Meltano, Gitpod, dbt, Superset.
- **Meltano Getting Started Project** (github.com/meltano/demo-project) — the project resulting from following the getting-started docs.

### 3. Sandbox projects

Beginner projects with mocks, local CSVs, or local databases — fully self-contained.

- **Meltano dbt Jaffle Shop** (github.com/meltano/jaffle-shop-template) — the dbt Jaffle Shop project in a Meltano context, with local DuckDB.
- **Meltano Extract Load Example** (github.com/sbalnojan/meltano-example-el) — AWS S3 CSV extract and load into PostgreSQL, fully mocked.
- **Meltano DB → DB Example** (github.com/sbalnojan/meltano-example-el-db) — extract from one Postgres database, load into another, fully mocked.

---

## How to use Jupyter with Meltano

Jupyter isn't a discoverable Meltano Hub plugin, so it's added as a local custom utility plugin. Steps:

1. Add a (local) custom Jupyter utility
2. Add Python libraries you'll need
3. Optionally expose database connection variables to the environment
4. Add Papermill or nbconvert to execute notebooks as data transformations, with custom commands
5. Execute notebooks and add them to a schedule

### 1. Add a custom Jupyter utility

Add as plugin type "utility" (jupyter serves multiple purposes). Choose the "classic notebook" (`jupyter` pip package) or `jupyterlab` (used in the examples below — swap the package name to switch).

```yaml
plugins:
  utilities: # meltano invoke jupyter will start up the lab...
  - name: jupyterlab
    namespace: jupyterlab
    pip_url: jupyterlab
    executable: jupyter
    commands:
      launch_ip0: #important for Mac users running Meltano inside Docker.
        args: lab --ip=0.0.0.0
        description: Start lab server, on any ip range for Mac users inside docker.
      launch:
        args: lab
        description: Start lab server
```

```bash
meltano install
meltano invoke jupyterlab:launch
```

Alternatively via CLI: `meltano add --custom utility jupyterlab` (interactive prompts).

### 2. Add Python libraries

Libraries generally fall into three categories: helper libraries (matplotlib, pandas), connection libraries (sqlalchemy, psycopg2), and notebook execution tools (nbconvert/papermill, handled in step 4). Extend `pip_url` with space-separated package names:

```yaml
plugins:
 utilities:
 - name: jupyterlab
   namespace: jupyterlab
   pip_url: jupyterlab pandas matplotlib sqlalchemy psycopg2-binary
   executable: jupyter
   commands:
     launch_ip0:
       args: lab --ip=0.0.0.0
       description: Start lab server, on any ip range for Mac users inside docker.
     launch:
       args: lab
       description: Start lab server
```

### 3. Optional: expose database connection variables

```yaml
default_environment: dev
environments:
- name: dev
  config:
  env:
      PG_HOST: postgres
      PG_PORT: "5432"
      PG_DB: demo
      PG_USER: admin
      PG_PWD: password
```

Accessible in notebooks via:
```python
import os

PG_HOST = os.getenv("PG_HOST", default=None)
PG_PORT = os.getenv("PG_PORT", default=None)
PG_DB = os.getenv("PG_DB", default=None)
PG_USER = os.getenv("PG_USER", default=None)
PG_PWD = os.getenv("PG_PWD", default=None)
```

### 4. Execute notebooks via nbconvert or papermill

Both Jupyter and JupyterLab offer `nbconvert` as the default execution option. Papermill (additional package) also allows parametrizing notebooks for execution; nbconvert only executes.

**nbconvert** — add a command (replace the notebook path with yours):
```yaml
  - name: jupyterlab
    namespace: jupyterlab
    pip_url: jupyterlab pandas matplotlib sqlalchemy psycopg2-binary papermill
    executable: jupyter
    commands:
      launch_ip0:
        args: lab --ip=0.0.0.0
        description: Start lab server, on any ip range for Mac users inside docker.
      launch:
        args: lab
        description: Start lab server
      execute:
        args: nbconvert --to notebook --execute notebook/sql_magic.ipynb
        description: Start lab server
```
Run with `meltano invoke jupyterlab:execute`.

**papermill** — use plugin inheritance to reuse the JupyterLab venv rather than reinstalling dependencies:
```yaml
  - name: papermill
    inherit_from: jupyterlab
    executable: papermill
    commands:
      execute:
        args: notebook/sql_magic.ipynb output/output.ipynb -p price_1 1000
        description: Start lab server, on any ip range for Mac users inside docker.
```
Adapt `args` to the notebook path, output path, and parameters — the example notebook has a `price_1` parameter overridable from the command line. See the papermill parameterization docs.

### 5. Execute & schedule notebooks

Putting it together:
```yaml
plugins:
  utilities: # meltano invoke jupyter will start up the lab...
  - name: jupyterlab
    namespace: jupyterlab
    pip_url: jupyterlab pandas matplotlib sqlalchemy psycopg2-binary papermill
    executable: jupyter
    commands:
      launch_ip0:
        args: lab --ip=0.0.0.0
        description: Start lab server, on any ip range for Mac users inside docker.
      launch:
        args: lab
        description: Start lab server
      execute:
        args: nbconvert --to notebook --execute notebook/sql_magic.ipynb
        description: Start lab server

  - name: papermill
    inherit_from: jupyterlab
    executable: papermill
    commands:
      execute:
        args: notebook/sql_magic.ipynb output/output.ipynb -p price_1 1000
        description: Start lab server, on any ip range for Mac users inside docker.
```
Execute with `meltano invoke papermill:execute` — this can be included in a Meltano pipeline/schedule.

---

## Video Tutorials & Demos

Advanced Meltano topics taught in Office Hour or Demo Day sessions on YouTube. Most are segments of a longer video. Topics covered:

- Combining Meltano & Lightdash (Meltano as EL+T with Lightdash, a lightweight BI tool integrating with dbt)
- Meltano Mappers (introduction to mappers, including the transferwise and meltano-map-transformer default mappers)
- tap-trello (introduction to the Trello tap)
- Meltano Slack Notifications (getting job notifications from Meltano into Slack)
- tap-auth0 (introduction to the Auth0 tap)
- tap-shopify (introduction to the Shopify tap)
- Meltano default environments (setting default environments in the project YAML)
- Meltano Incremental Runs (the incremental runs feature of `meltano run`, contrasted with `meltano elt`)
- Superset import datasources (automatic import of dbt database connections/sources into Superset via Meltano)
- Meltano, AD, and dbt audit tables (using Meltano to update Active Directory accounts)
- Meltano Plugin Inheritance Optimization (optimizing plugin inheritance, sharing/unsharing venvs)
- Meltano Lock Files (how plugin lock files work)
- Meltano Jobs & Tasks (introducing the `meltano job` command)
- Meltano Kedro plugin (how the Meltano Kedro plugin works)
- Meltano dbt-osmosis (how dbt-osmosis works together with Meltano)
- Meltano Interactive Mode (the Meltano interactive config mode explained)
- Meltano Container Spec (using the container spec to run commands in containers)
- Meltano Great Expectations (introducing Great Expectations with Meltano)
- Meltano Mapper Plugins (how mapper plugins work, focused on the default transferwise plugin)
