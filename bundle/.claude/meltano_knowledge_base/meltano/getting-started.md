# Getting Started with Meltano

Installation instructions plus a condensed, step-by-step walkthrough: create a project, extract data from GitHub, load it into JSON/PostgreSQL, and transform it with dbt.

## Installation

Meltano supports all versions of Python that have not yet reached end-of-life. Check your version first:

```bash
python --version
```

Not all plugins support the latest Python versions.

### Using uv (recommended)

[`uv`](https://docs.astral.sh/uv) is a Python package and project manager written in Rust. It makes it easy to install a Python-based tool like Meltano in an isolated virtual environment.

```console
$ uv tool install meltano
Installed 1 executable: meltano
```

### Using pipx

Since Meltano is an application, it should always be installed into a clean virtual environment without other packages installed alongside it. [`pipx`](https://pypa.github.io/pipx/) installs executable Python applications (such as Meltano) into their own virtual environments.

```console
$ pipx install "meltano"
successfully installed meltano
```

### Using Docker

The `meltano/meltano` Docker image on Docker Hub comes with Python and Meltano pre-installed.

- **Slim images** (recommended): `-slim` suffix, e.g. `latest-slim` — optimized size, includes cloud storage and PostgreSQL support.
- **Full images**: default tags like `latest` — includes all database connectors and build tools.

Images for specific versions are tagged `v<major>.<minor>.<patch>`, e.g. `v3.8.0` or `v3.8.0-slim`. Add a `-python3.X` suffix to change the Python version, e.g. `latest-python3.13-slim`. Omit the patch/minor version to get the latest, e.g. `v3-slim`.

```console
$ docker pull meltano/meltano:latest-slim
$ docker run meltano/meltano:latest-slim --version
meltano, version 3.9.1
```

### Using pip

```console
$ pip install --upgrade pip
$ pip install "meltano"
successfully installed meltano
```

To avoid dependency conflicts, ensure Meltano is installed into a clean Python virtual environment — use the `--require-virtualenv` flag or `PIP_REQUIRE_VIRTUALENV=1` environment variable. In ephemeral CI or container-based deployments where Meltano is the main application, installing it globally may be preferred.

### Upgrading

Use `uv tool upgrade meltano`, `pipx upgrade meltano`, `pip install --upgrade meltano`, or pull the latest Docker image.

---

## Step 1: Create Your Meltano Project

Create and navigate to a directory to hold your Meltano projects:

```bash
mkdir meltano-projects
cd meltano-projects
```

Initialize a new project:

```bash
meltano init my-meltano-project
```

Example output:

```console
$ meltano init my-new-project
Created my-new-project
Creating project files...
  my-new-project/
  |-- .meltano
  |-- meltano.yml
  |-- README.md
  |-- requirements.txt
  |-- output/.gitignore
  |-- .gitignore
  |-- extract/.gitkeep
  |-- load/.gitkeep
  |-- transform/.gitkeep
  |-- analyze/.gitkeep
  |-- notebook/.gitkeep
  |-- orchestrate/.gitkeep
Creating system database...  Done!
... Project my-new-project has been created!

Meltano Environments initialized with dev, staging, and prod.
```

This creates a `meltano.yml` project file that looks like:

```yml
default_environment: dev
project_id: <unique-GUID>
environments:
- name: dev
- name: staging
- name: prod
```

Navigate into the new project directory:

```bash
cd my-meltano-project
```

Optionally, initialize Git for version control:

```bash
git init
git add --all
git commit -m 'Initial Meltano project'
```

### View and activate environments

```bash
meltano environment list
```

Activate an environment for your shell session:

```bash
export MELTANO_ENVIRONMENT=dev
```

Or on Windows PowerShell:

```powershell
$env:MELTANO_ENVIRONMENT="dev"
```

Alternatively, pass `--environment=dev` to each `meltano` command. Add a new environment with:

```bash
meltano environment add <environment name>
```

---

## Step 2: Add an Extractor (Connect to a Data Source)

This walkthrough uses GitHub as the example source. You'll need a [GitHub personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token).

Add the extractor (plugin type is auto-detected):

```bash
meltano add tap-github
```

Example output:

```console
$ meltano add tap-github
Added extractor 'tap-github' to your Meltano project
Variant:        meltanolabs (default)
Repository:     https://github.com/meltanolabs/tap-github
Documentation:  https://hub.meltano.com/extractors/tap-github--meltanolabs

2024-01-01T00:25:40.604941Z [info     ] Installing extractor 'tap-github'
2024-01-01T00:25:53.152127Z [info     ] Installed extractor 'tap-github'
```

This adds the plugin to `meltano.yml`:

```yml
plugins:
extractors:
  - name: tap-github
    variant: meltanolabs
    pip_url: git+https://github.com/MeltanoLabs/tap-github.git
```

Verify the install:

```bash
meltano invoke tap-github --help
```

### Configure the extractor

The simplest way to configure a plugin is interactively:

```bash
meltano config set tap-github --interactive
```

Follow the prompts to fill in settings such as `repositories` (e.g. `["meltano/meltano"]`), `start_date`, and `auth_token`.

This adds non-sensitive config to `meltano.yml`:

```yml
plugins:
  extractors:
    - name: tap-github
      config:
        start_date: '2024-01-01'
        repositories:
        - meltano/meltano
```

Sensitive values (like the auth token) go into `.env`:

```yml
TAP_GITHUB_AUTH_TOKEN='ghp_XXX' # your token!
```

Check the config:

```bash
meltano config list tap-github
```

### Select entities and attributes to extract

List what's available:

```bash
meltano select tap-github --list --all
```

Select specific entities/attributes:

```bash
meltano select tap-github commits url
meltano select tap-github commits sha
meltano select tap-github commits commit_timestamp
```

This adds selection rules to `meltano.yml`:

```yml
default_environment: dev
environments:
- name: dev
- name: staging
- name: prod
project_id: YOUR_ID
plugins:
  extractors:
  - name: tap-github
    variant: meltanolabs
    pip_url: git+https://github.com/MeltanoLabs/tap-github.git
    config:
      start_date: '2024-01-01'
      repositories:
      - sbalnojan/meltano-lightdash
    select:
    - commits.url
    - commits.sha
    - commits.commit_timestamp
```

Double-check the selection:

```bash
meltano select tap-github --list
```

---

## Step 3: Add a Loader (JSON, for a Quick Test)

To verify extraction works before setting up a real database, add a JSON target (requires zero configuration):

```bash
meltano add target-jsonl
```

```console
$ meltano add target-jsonl
Added loader 'target-jsonl' to your Meltano project
Variant:        andyh1203 (default)
```

Run the pipeline:

```bash
meltano run tap-github target-jsonl
```

```console
$ meltano run tap-github target-jsonl
2024-09-19T13:53:36.403099Z [info     ] Environment 'dev' is active
2024-09-19T13:53:41.071885Z [warning  ] No state was found, complete import.
2024-09-19T13:53:43.054384Z [info     ] INFO Starting sync of repository: sbalnojan/meltano-lightdash
```

Check the output:

```bash
cat output/commits.jsonl
```

```console
{"sha": "409bdd601e0531833665f538bccecd0f69e101c0", ..., "commit_timestamp": "2024-09-14T12:41:21Z"}
```

---

## Step 4: Load Into PostgreSQL

Start a local PostgreSQL container:

```bash
docker run --name meltano_postgres -p 5432:5432 -e POSTGRES_USER=meltano -e POSTGRES_PASSWORD=password -d postgres
```

Connection details: host `localhost`, port `5432`, database `postgres`, user `meltano`, password `password`.

### Add and configure target-postgres

```bash
meltano add target-postgres --variant=meltanolabs
```

Check available settings:

```bash
meltano config list target-postgres
```

Set the required values:

```console
$ meltano config set target-postgres user meltano
$ meltano config set target-postgres password password
$ meltano config set target-postgres database postgres
$ meltano config set target-postgres add_record_metadata True
$ meltano config set target-postgres host localhost
```

Non-sensitive config lands in `meltano.yml`:

```yml
plugins:
  loaders:
    - name: target-postgres
      variant: meltanolabs
      pip_url: git+https://github.com/MeltanoLabs/target-postgres.git
      config:
        user: meltano
        database: postgres
        add_record_metadata: true
        host: localhost
```

Sensitive config (like `password`) goes to `.env`. Verify full config, including defaults:

```bash
meltano config print target-postgres
```

By default the destination schema is named after the tap (e.g. `tap_github`). Override this with `default_target_schema`.

### Run the pipeline

```bash
meltano run tap-github target-postgres
```

```console
$ meltano run tap-github target-postgres
2024-09-20T13:16:13.885045Z [warning  ] No state was found, complete import.
2024-09-20T13:16:16.435885Z [info     ] message=Schema 'tap_github' does not exist. Creating...
2024-09-20T13:16:16.632945Z [info     ] message=Table '"commits"' does not exist. Creating...
2024-09-20T13:16:16.729076Z [info     ] message=Loading 21 rows into 'tap_github."commits"'
```

The `tap_github` schema in Postgres should now contain a `commits` table.

---

## Step 5: Transform Data With dbt

Get all attributes from commits (not just the three selected earlier):

```bash
meltano select tap-github commits "*"
```

This appends to the `select` list in `meltano.yml`. Refresh the tables with a full refresh:

```bash
meltano run --full-refresh tap-github target-postgres
```

### Install and initialize the dbt utility

dbt utilities are adapter-specific (e.g. `dbt-postgres`, `dbt-snowflake`). Install the one matching your warehouse:

```bash
meltano add dbt-postgres
```

Populate the dbt project scaffold:

```bash
meltano invoke dbt-postgres:initialize
```

```console
$ meltano invoke dbt-postgres:initialize
creating dbt profiles directory path=.../my-meltano-project/transform/profiles/postgres
dbt initialized  dbt_ext_type=postgres ...
```

> If installing `dbt-postgres` requires building `psycopg2` from source, constrain it in the plugin's `pip_url`:
> ```yaml
>   utilities:
>   - name: dbt-postgres
>     pip_url: dbt-core dbt-postgres meltano-dbt-ext~=0.5.0
> ```

### Configure dbt

```console
$ meltano config set dbt-postgres host localhost
$ meltano config set dbt-postgres port 5432
$ meltano config set dbt-postgres user meltano
$ meltano config set dbt-postgres password password
$ meltano config set dbt-postgres dbname postgres
$ meltano config set dbt-postgres schema analytics
```

Resulting `meltano.yml` (sensitive values live in `.env`):

```yaml
  utilities:
  - name: dbt-postgres
    config:
      host: localhost
      port: 5432
      user: meltano
      dbname: postgres
      schema: analytics
```

### Define the dbt source

Create the models directory and a `source.yml` describing where the raw data landed:

```bash
mkdir transform/models/tap_github
```

`transform/models/tap_github/source.yml`:

```yaml
config-version: 2
version: 2
sources:
  - name: tap_github     # the name we want to reference this source by
    schema: tap_github   # the schema the raw data was loaded into
    tables:
      - name: commits
```

### Add a transformed model

`transform/models/tap_github/authors.sql`:

```sql
{{
  config(
    materialized='table'
  )
}}

with base as (
    select *
    from {{ source('tap_github', 'commits') }}
)
select distinct (commit -> 'author' -> 'name') as authors
from base
```

### Run the transformation

```bash
meltano invoke dbt-postgres:run
```

```console
$ meltano invoke dbt-postgres:run
Extension executing `dbt run`...
20:45:15  Found 1 model, 0 tests, 0 snapshots, ...
20:45:15  1 of 1 START sql table model analytics.authors ................................. [RUN]
20:45:15  1 of 1 OK created sql table model analytics.authors ............................ [SELECT 1 in 0.14s]
20:45:15  Done. PASS=1 WARN=0 ERROR=0 SKIP=0 TOTAL=1
```

> If dbt complains about cleaning files outside the project directory, add to `meltano.yml`:
> ```yaml
> env:
>   DBT_CLEAN_PROJECT_FILES_ONLY: "false"
> ```

Check the `analytics` schema in Postgres for a populated `authors` table.

### Run the complete pipeline end-to-end

To verify the full pipeline works together, drop the existing tables:

```bash
docker exec meltano_postgres psql -d postgres -U meltano -c 'DROP TABLE tap_github.commits; DROP TABLE analytics.authors;'
```

Then run extract, load, and transform in one command with a full refresh:

```bash
meltano run --full-refresh tap-github target-postgres dbt-postgres:run
```

---

## Next Steps

### Schedule pipelines to run regularly

```bash
meltano schedule add gitlab-to-postgres --extractor tap-gitlab --loader target-postgres --interval @daily
```

The `pipeline name` argument corresponds to the `--state-id` option on `meltano el`, identifying related EL(T) runs for incremental replication state. Use the same name across manual and scheduled runs so state carries over.

This adds a schedule to `meltano.yml`:

```yml
schedules:
  - name: gitlab-to-postgres
    extractor: tap-gitlab
    loader: target-postgres
    transform: skip
    interval: "@daily"
```

Verify and run manually:

```bash
meltano schedule list
meltano schedule run
```

Add Airflow to actually execute schedules:

```bash
meltano add airflow
```

Start the scheduler and (optionally) the web UI:

```bash
meltano invoke airflow scheduler
meltano invoke airflow webserver
```

Create an admin user:

```bash
meltano invoke airflow users create --username melty \
  --firstname melty \
  --lastname meltano \
  --role Admin \
  --password melty \
  --email melty@meltano.com
```

The Airflow web interface is available at `http://localhost:8080`.

### Other next steps

- Analyze data with [Superset](https://superset.apache.org/).
- Containerize your project for deployment.
- Deploy your pipelines to production.

### Incremental replication and full refresh

Running `meltano run` again automatically picks up where the previous run left off (if the extractor supports incremental replication and you have an active environment). Meltano tracks state using a State ID generated from the extractor name, loader name, and active environment name. To ignore stored state and re-extract everything, use `--full-refresh` or set `MELTANO_RUN_FULL_REFRESH=1`.

Other useful commands:
- `meltano el` — a more rigid command for running only EL pipelines.
- `meltano invoke` — executes a single plugin at a time; useful for debugging.
- `meltano state get <state_id>` — view the state generated by the most recent run.
