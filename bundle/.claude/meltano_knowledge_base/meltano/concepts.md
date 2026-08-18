# Meltano Concepts

Reference documentation for Meltano's core concepts: projects, plugins, environments, state backends, and Python virtual environments.

## Projects

At the core of the Meltano experience is your Meltano project: the single source of truth for how data should be integrated and transformed, how pipelines are orchestrated, and how plugins are configured. A project is just a directory of text-based files, so it can be treated like any software project — version control, code review, CI/CD all apply.

Initialize a new project with `meltano init`.

### `meltano.yml` project file

A Meltano project must contain a `meltano.yml` file. The only required property is `version` (currently always `1`). A formal JSON Schema is available on SchemaStore.org.

**Project-level configuration** sits at the root of the file. A newly initialized project has a few environments populated to get started.

#### Plugins in `meltano.yml`

Plugins are defined under the `plugins` property, in an array named after the plugin type (e.g. `extractors`, `loaders`). Every plugin needs:

1. a `name` unique among plugins of the same type,
2. a base plugin description (what package, what settings/capabilities it supports), and
3. configuration.

A base plugin description consists of `pip_url`, `executable`, `capabilities`, and `settings`. There are three kinds of plugin definitions:

**Inheriting** — has `inherit_from`, inherits base description from another project plugin or a discoverable plugin:

```yaml title="meltano.yml"
plugins:
  extractors:
  - name: tap-postgres          # Shadows discoverable `tap-postgres`
  - name: tap-postgres--billing
    inherit_from: tap-postgres  # Inherits from project's `tap-postgres`
  - name: tap-bigquery--events
    inherit_from: tap-bigquery  # Inherits from discoverable `tap-bigquery`
```

Configuration is inherited as defaults and can be overridden:

```yaml title="meltano.yml"
plugins:
  extractors:
  - name: tap-google-analytics
    variant: meltano
    config:
      key_file_location: client_secrets.json
      start_date: '2020-10-01T00:00:00Z'
  - name: tap-ga--view-foo
    inherit_from: tap-google-analytics
    config:
      # `key_file_location` and `start_date` are inherited
      view_id: 123456
  - name: tap-ga--view-bar
    inherit_from: tap-google-analytics
    config:
      # `key_file_location` is inherited
      start_date: '2020-12-01T00:00:00Z' # overridden
      view_id: 789012
```

If a `variant` property is present, only discoverable plugins are considered as the inheritance source, since only those can have multiple variants:

```yaml title="meltano.yml"
plugins:
  loaders:
  - name: target-snowflake          # Shadows discoverable `target-snowflake`
    variant: datamill-co
  - name: target-snowflake--derived
    inherit_from: target-snowflake  # Inherits from project's `target-snowflake`
  - name: target-snowflake--transferwise
    inherit_from: target-snowflake  # Inherits from discoverable `target-snowflake`
    variant: transferwise
```

**Custom** — has `namespace` (no `inherit_from`), explicitly defines its base plugin description:

```yaml title="meltano.yml"
plugins:
  extractors:
  - name: tap-covid-19
    namespace: tap_covid_19
    pip_url: tap-covid-19
    executable: tap-covid-19
    capabilities:
    - catalog
    - discover
    - state
    settings:
    - name: api_token
    - name: user_agent
    - name: start_date
```

**Shadowing** — has neither `inherit_from` nor `namespace`; implicitly inherits from the discoverable plugin of the same name:

```yaml title="meltano.yml"
plugins:
  extractors:
  - name: tap-gitlab
```

If multiple variants of a discoverable plugin exist, pick one with `variant`:

```yaml title="meltano.yml"
plugins:
  extractors:
  - name: tap-gitlab
    variant: meltano
```

If no `variant` is specified, the *original* variant is used (not necessarily the recommended *default* variant for new users).

#### Plugin configuration

Stored under a `config` property. Extras are stored alongside, outside `config`:

```yaml
extractors:
- name: tap-example
  config:
    example_setting: value
  example_extra: value
```

#### Plugin commands

Defined via `commands`. Keys are command names; values are arguments passed to the plugin executable. Can reference configuration dynamically via environment variable form:

```yaml
utilities:
- name: dbt-snowflake
  variant: dbt-labs
  commands:
    my_models:
      args: run --select +my_model_name
      description: Run dbt, selecting model `my_model_name` and all upstream models.
```

Commands can specify documentation and an alternative executable:

```yaml
- name: dagster
  variant: quantile-development
  commands:
    start:
      args: -f $REPOSITORY_DIR/repository.py
      description: Start Dagster.
      executable: dagit_invoker
```

Commands can also specify a `container_spec` for containerized execution (run with `--containers`).

### Jobs

Predefined pipelines under `jobs`, typically created with `meltano job`. A job needs a `name` and one or more `tasks`:

```yaml
jobs:
  - name: tap-foo-to-target-bar-dbt
    tasks:
      - tap-foo target-bar dbt:run
  - name: tap-foo-to-targets-bar-and-baz
    tasks:
      - tap-foo target-bar
      - tap-foo target-baz
```

### Schedules

Pipeline schedules under `schedules`, typically created with `meltano schedule`. Needs a `name`, `job`, and `interval`:

```yaml
schedules:
  - name: foo-to-bar
    job: tap-foo-to-target
    interval: "@hourly"
```

Or provide `extractor`, `loader`, `transform` directly instead of `job`:

```yaml
- name: foo-to-bar-elt
  extractor: tap-foo
  loader: target-bar
  transform: skip
  interval: "@hourly"
```

Pipeline-specific configuration via an `env` dictionary:

```yaml
schedules:
- name: foo-to-bar
  job: tap-foo-to-target-bat
  interval: "@hourly"
  env:
    TAP_FOO_BAR: bar
    TAP_FOO_BAZ: baz
```

### Multiple YAML files

Break config into multiple `.yml` files listed (directly or via glob) under `include_paths`:

```yaml
include_paths:
  - "./subconfig_[0-9].yml"
  - "./*/subconfig_[0-9].yml"
  - "./*/**/subconfig_[0-9].yml"
```

Currently supported elements in subfiles: plugins, schedules, environments. New config elements added via CLI always go into `meltano.yml`, not subfiles.

### Annotations

`annotations` is a dictionary mapping tool/vendor names to arbitrary dictionaries, for integration with third-party tools:

```yaml
annotations:
  arbitrary-third-party-tool: {
    # Configuration for the third party tool
  }
```

Meltano's core library/CLI never reads or acts on `annotations` — it's inert extra data. Supported at: the top level, and in job/schedule/environment/plugin/environment-plugin/setting definitions.

### `.gitignore`

A newly initialized project includes a `.gitignore` so environment-specific/sensitive config in `.meltano/` and `.env` isn't leaked. Everything else should be checked into version control.

### `.env`

Optional file for environment variables used to configure Meltano and plugins — typically environment-specific or sensitive config that shouldn't go in `meltano.yml`. `meltano config set <plugin>` automatically stores config in `meltano.yml` or `.env` as appropriate. Included in `.gitignore` by default.

### `.meltano` directory

Internal files, specific to the environment Meltano runs in (not checked into version control). `$MELTANO_SYS_DIR_ROOT` can replace `$MELTANO_PROJECT_ROOT/.meltano`. Notable contents:

- `.meltano/meltano.db` — default SQLite system database.
- `.meltano/logs/elt/<state_id>/<run_id>/elt.log` — output logs for a pipeline run.
- `.meltano/run/bin` — symlink to the most recently used `meltano` executable.
- `.meltano/run/elt/<state_id>/<run_id>/` — pipeline-specific generated plugin config files (catalog, properties, state).
- `.meltano/run/<plugin name>/` — config files generated by `meltano invoke`.
- `.meltano/<plugin type>/<plugin name>/venv/` — the plugin's Python virtual environment.

### System database

Metadata storage, defaults to SQLite (`meltano.db`) inside `.meltano/`, configurable via the `database_uri` setting. Key tables:

- `runs` — one row per `meltano el`/`elt`/`run` pipeline run: started/ended timestamps, incremental replication state.
- `plugin_settings` — plugin configuration set via `meltano config set <plugin>` when the project is deployed read-only.

#### Supported database backends

| Database | Supported Versions | Extra Requirement | Example URL |
|---|---|---|---|
| SQLite | `3.25.0`+ | None | `sqlite:///$MELTANO_SYS_DIR_ROOT/meltano.db` (default) |
| PostgreSQL | `13`+ | `postgres` extra | `postgresql+psycopg://<user>:<password>@<host>:<port>/<dbname>` |
| MS SQL Server | `2019`+ | `mssql` extra | `mssql+pymssql://<user>:<password>@<freetds_name>/?charset=utf8` |

MySQL and Snowflake support are tracked as open feature requests.

---

## Plugins

Meltano projects and pipelines are composed of plugins of different types, most notably **extractors** (Singer taps), **loaders** (Singer targets), and **utilities** (dbt, Airflow/Dagster, etc. via MeltanoHub).

### Project plugins

To use a package as a plugin, Meltano needs: (1) where to find the package (pip package name, Git URL, or local path), (2) what settings it supports, (3) what capabilities it supports, and (4) its configuration when invoked. The package location + metadata make up the **base plugin description**; a project's plugin extends this with specific configuration and a unique name.

Different configurations of the same package are represented as separate plugins with unique names — e.g. `tap-postgres--billing` and `tap-postgres--events` both derived from base `tap-postgres`.

Each plugin can: inherit its base description from a discoverable plugin, define its own base description (custom plugin), or inherit both base description and configuration from another project plugin (plugin inheritance).

### Discoverable plugins

Base plugin descriptions for popular extractors, loaders, and other plugins are collected on [Meltano Hub](https://hub.meltano.com), making them supported out of the box.

#### Variants

Multiple alternative implementations of a tap/target may exist under the same name (`tap-<source>` / `target-<destination>`) but vary in behavior, quality, and settings — these are "variants." Every discoverable plugin has a default variant recommended for new users; users with existing experience with a different variant can choose it explicitly.

### Custom plugins

If a package's base plugin description isn't discoverable yet, define it yourself using a custom plugin definition (`namespace` property). Consider contributing the description to Meltano Hub afterward.

### Plugin inheritance

To use the same base plugin multiple times with different configurations, add a new plugin inheriting from an existing one. The new plugin inherits the parent's base description and configuration as defaults, overridable as needed.

For performance, inherited plugins with an identical `pip_url` to their parent share the parent's Python virtualenv. To get a separate virtualenv, set a different `pip_url` on the inherited plugin.

### Lock artifacts

`meltano add` downloads the discoverable plugin definition and adds it to the project under `plugins/<plugin_type>/<plugin_name>--<variant_name>.lock`, stabilizing and version-controlling the plugin's definition. Custom and inherited plugins do not get a lock file.

### Plugin types

- **Extractors** — pull data out of arbitrary data sources.
- **Mappers** — perform stream map transforms on data between extractors and loaders.
- **Loaders** — load extracted data into arbitrary data destinations.
- **Utilities** — arbitrary tasks provided by pip packages with executables. Transformers and orchestrators are being folded into utilities.
- **File bundles** — bundle files you may want in your project.
- **Orchestrators** (transitioning to Utilities) — orchestrate a project's scheduled pipelines.
- **Transformers** (transitioning to Utilities) — run transforms.
- **Transforms** (deprecated) — transform data that has been loaded into a warehouse.

#### Extractors

Pip packages used by `meltano run`/`meltano invoke` for data integration; implement the [Singer specification](https://hub.meltano.com/singer/spec) (Singer taps).

**Extras:** `catalog`, `load_schema`, `metadata`, `schema`, `select`, `select_filter`, `state`, `use_cached_catalog`.

- **`catalog`** (setting `_catalog`, env `<EXTRACTOR>__CATALOG`) — path to a catalog file to use instead of running discovery mode. Selection filter rules still apply on top.
  ```yaml
  extractors:
  - name: tap-gitlab
    catalog: extract/tap-gitlab.catalog.json
  ```

- **`load_schema`** (setting `_load_schema`, env `<EXTRACTOR>__LOAD_SCHEMA`, default `$MELTANO_EXTRACTOR_NAMESPACE`) — target database schema name for loaders that support schemas (Postgres, Snowflake). Referenced from loader config via `MELTANO_EXTRACT__LOAD_SCHEMA`.
  ```yaml
  extractors:
  - name: tap-gitlab
    load_schema: gitlab_data
  ```

- **`metadata`** (setting `_metadata`/`metadata`, env `<EXTRACTOR>__METADATA`, default `{}`) — Singer stream/property metadata rules applied to the discovered catalog. Not applied to manually-provided catalogs. Supports Unix glob wildcards in stream/property identifiers.
  ```yaml
  extractors:
  - name: tap-postgres
    metadata:
      some_stream_id:
        replication-method: INCREMENTAL
        replication-key: created_at
        created_at:
          is-replication-key: true
  ```
  Common metadata keys: `key-properties` (unique identifier columns), `replication-key` (bookmark column), `replication-method` (`FULL_TABLE`, `INCREMENTAL`, or `LOG_BASED` if supported).

- **`schema`** (setting `_schema`, env `<EXTRACTOR>__SCHEMA`, default `{}`) — JSON Schema override rules applied to the discovered catalog. If a schema is specified for a property that doesn't exist yet, it's added to the catalog — useful for taps without discovery (e.g. `tap-dynamodb`).
  ```yaml
  extractors:
  - name: tap-postgres
    schema:
      some_stream_id:
        created_at:
          type: ["string", "null"]
          format: date-time
  ```

- **`select`** (setting `_select`, env `<EXTRACTOR>__SELECT`, default `["*.*"]`) — array of stream/property selection rules applied to the discovered catalog. A rule can be stream-only (`"users"`, equivalent to `"users.*"`) or stream.property (`"users.id"`). Prefix with `!` to exclude. Supports wildcards.
  ```yaml
  extractors:
  - name: tap-gitlab
    select:
    - project_members      # Stream-only: all properties
    - commits.id
    - commits.author_name
    - issues.*
  ```
  Escape literal dots in stream names with backslash: `animals\.data.id`.

- **`select_filter`** (setting `_select_filter`, env `<EXTRACTOR>__SELECT_FILTER`, default `[]`) — stream-level filter applied *after* schema/select/metadata rules, via `meltano el --select`/`--exclude`. Filters which streams run without changing the underlying `select` configuration — useful for parallelization, testing, and conditional runs.
  ```yaml
  extractors:
  - name: tap-gitlab
    select:
    - project_members
    - commits.id
    - commits.author_name
    - issues.*
    select_filter:
    - commits   # only process commits + issues; project_members filtered out
    - issues
  ```
  ```bash
  meltano el tap-gitlab target-jsonl --select commits        # only commits
  meltano el tap-gitlab target-jsonl --exclude logs           # all except logs
  ```

  **`select` vs `select_filter`:**

  | `select` | `select_filter` |
  |---|---|
  | Stream & property-level: which streams/properties to include | Stream-level: which entire streams to include/exclude |
  | Defines what data fields you want | Filters `select`-configured streams for a specific run |
  | Does not preserve — it *is* the selection | Preserves existing `select` configuration, filters on top |

- **`state`** (setting `_state`, env `<EXTRACTOR>__STATE`, `meltano el --state`) — path to a state file to use instead of automatic lookup by State ID.
  ```yaml
  extractors:
  - name: tap-gitlab
    state: extract/tap-gitlab.state.json
  ```

- **`use_cached_catalog`** (setting `_use_cached_catalog`, env `<EXTRACTOR>__USE_CACHED_CATALOG`, default `True`) — set `False` to force fresh discovery every run instead of using Meltano's cached catalog. Useful when schema changes affect discovery, or for taps with dynamic discovery (e.g. `tap-salesforce`).

#### Loaders

Pip packages used by `meltano el` for data integration; implement the Singer spec (Singer targets).

**Extras:** `dialect`.

- **`dialect`** (setting `_dialect`, env `<LOADER>__DIALECT`, default `$MELTANO_LOADER_NAMESPACE`) — the target database's dialect name, so transformers in the same pipeline know what to connect to. Referenced via `MELTANO_LOAD__DIALECT`; used as the default for dbt's `target` setting (should match a target name in `transform/profile/profiles.yml`).
  ```yaml
  loaders:
  - name: target-example-db
    dialect: example-db
  ```

#### Transforms (deprecated)

dbt packages containing dbt models, used by `meltano el`. Being phased out in favor of calling dbt packages directly. Adding one via `meltano add` adds the package's Git repo to `transform/packages.yml` and enables it in `transform/dbt_project.yml`.

**Extras:** `package_name`, `vars`.

- **`package_name`** (setting `_package_name`, env `<TRANSFORM>__PACKAGE_NAME`, default `$MELTANO_TRANSFORM_NAMESPACE`) — the dbt package's internal project name (`name` in `dbt_project.yml`). Referenced via `MELTANO_TRANSFORM__PACKAGE_NAME`.
  ```yaml
  transforms:
  - name: dbt-facebook-ads
    namespace: tap_facebook
    package_name: facebook_ads
  ```

- **`vars`** (setting `_vars`, env `<TRANSFORM>__VARS`, default `{}`) — dbt model variables referenced via the `var` function. Since dbt handles these, use dbt's `env_var` function rather than `$VAR`/`${VAR}`.
  ```yaml
  transforms:
  - name: tap-gitlab
    vars:
      schema: '{{ env_var(''DBT_SOURCE_SCHEMA'') }}'
  ```

#### Orchestrators (transitioning to Utilities)

Responsible for orchestrating a project's scheduled pipelines. Meltano supports Apache Airflow out of the box, or any tool that can read `meltano schedule list --format=json` output and execute each pipeline's `meltano run` command on a schedule. Adding the `airflow` utility auto-adds its related file bundle.

#### Transformers (transitioning to Utilities)

Used by `meltano run` for data transformation; run transforms. Meltano supports dbt out of the box. Adding the `dbt` transformer auto-adds its related file bundle.

#### File bundles

Bundle files you may want in your project. Adding one via `meltano add` adds the bundled files automatically. The bundle itself is only added to `meltano.yml` if it contains files managed by the bundle (see `update` extra).

**Extras:** `update`.

- **`update`** (setting `_update`, env `<BUNDLE>__UPDATE`, default `{}`) — maps file paths (relative to project root, glob patterns supported) to booleans. `True` means the file is managed by the bundle and updated automatically on `meltano upgrade`.
  ```yaml
  files:
  - name: dbt
    update:
      transform/dbt_project.yml: false
      profiles/*.yml: true
  ```
  If a path starts with `*`, quote it: `'*.yml': true`.

#### Utilities

Represents all non-EL plugins (formerly transformer/orchestrator types, e.g. dbt, Airflow, Dagster, now included as utilities). Any pip package exposing an executable can be added as a utility. Meltano's Extension Developer Kit (EDK) can integrate existing data tools.

**Custom utilities:**
```bash
meltano add --custom utility yoyo
(namespace): yoyo
(pip_url): yoyo-migrations
(executable): yoyo
```
Invoke with:
```bash
meltano invoke yoyo new ./migrations -m "Add column to foo"
```
Benefit over `pip install`/`requirements.txt`: packages installed this way get Meltano's virtual environment isolation, avoiding dependency conflicts.

#### Mappers

Transform/manipulate data after extraction and before loading — alias streams/properties, filter records, transform properties inline (type conversion, PII sanitizing), remove or add properties. Only available via `meltano run`.

Install like any plugin:
```bash
meltano add mapper transform-field
```

Mappers aren't invoked directly — you define `mappings` by name, each with its own config object, then reference the mapping name (not the plugin name) in a `meltano run` invocation:

```yaml
mappers:
  - name: transform-field
    variant: transferwise
    pip_url: pipelinewise-transform-field
    executable: transform-field
    mappings:
    - name: hide-gitlab-secrets
      config:
        transformations:
          - field_id: "author_email"
            tap_stream_name: "commits"
            type: "MASK-HIDDEN"
          - field_id: "committer_email"
            tap_stream_name: "commits"
            type: "MASK-HIDDEN"
    - name: null-created-at
      config:
        transformations:
          - field_id: "created_at"
            tap_stream_name: "accounts"
            type: "SET-NULL"
```

```bash
$ meltano run tap-gitlab hide-gitlab-secrets target-jsonl
$ meltano run tap-someapi null-created-at target-jsonl
```

Multiple mappings can be chained in series, even reusing the same plugin at multiple points, since each executes in its own process:

```bash
$ tap-someapi fix-null-id fix-country-code target-jsonl
$ tap-someapi fix-null-country set-region-from-country mask-id-if-eu target-jsonl
```

---

## Environments

Environments let you define custom layers of configuration within a project, so you can run the same commands against multiple environments by passing a single variable or CLI option — reducing the environment variables you need to manage and eliminating juggling multiple `.env` files.

```yaml
default_environment: dev
project_id: 9f8ac2b3-58ae-4db0-b20a-d9f5431c5d93
environments:
  - name: prod
    config:
      plugins:
        extractors:
          - name: tap-github
            config:
              organizations: [Meltano]
            select: ["*.*"]
        loaders:
          - name: target-snowflake
            config:
              dbname: prod
              warehouse: prod_wh
              batch_size_rows: 100000
    env:
      SOME_PROD_ONLY_SETTING: abc
  - name: dev
    config:
      plugins:
        extractors:
          - name: tap-github
            config:
              organizations: [MeltanoLabs]
            select: ["repositories.*"]
        loaders:
          - name: target-snowflake
            config:
              dbname: dev
              warehouse: dev_wh
              batch_size_rows: 1000
    state_id_suffix: ${CUSTOM_SUFFIX}
plugins:
  extractors:
  - name: tap-github
    variant: meltanolabs
    pip_url: git+https://github.com/MeltanoLabs/tap-github.git
    config:
      start_date: '2024-01-01'
  loaders:
  - name: target-snowflake
    variant: meltanolabs
    pip_url: meltanolabs-target-snowflake
    config:
      account: meltano
      add_record_metadata: true
      password: ${SNOWFLAKE_PASSWORD}
```

**Environments vs Python Virtual Environments:** For installable Python plugins (those with a `pip_url`) configured across multiple Environments, the same Python virtualenv and executable are reused. To install different versions of the same plugin, use plugin inheritance with a different `pip_url` on the inherited plugin.

### Inheritance

Environments are most powerful when inheriting from a base plugin definition — configuration set in an environment adds to or overrides the base plugin config, enabling reuse of common configuration while making it easy to switch per environment.

### The `env` mapping

An environment can define an `env` mapping injected into the plugin(s) environment at runtime. Only project-set variables referenced in the mapping are expanded: `MELTANO_PROJECT_ROOT`, `MELTANO_SYS_DIR_ROOT`, `MELTANO_ENVIRONMENT`, `MELTANO_USER_AGENT`.

```yaml
environments:
  - name: dev
    env:
      MY_ENV_VAR: $MELTANO_PROJECT_ROOT/path/to/a/file.json
```

### State ID suffix

An environment can define `state_id_suffix` — a custom suffix appended (with a colon prefix) to the generated state ID for each extractor/loader pair passed to `meltano run`. Full ID format: `<environment_name>:<tap_name>-to-<target_name>:<state_id_suffix>`. Supports interpolation of environment variables, useful for dynamic state IDs across multiple invocations of the same environment and EL pair.

### Activation

Pass `--environment=<ENV>` to the CLI, or set `MELTANO_ENVIRONMENT=<ENV>`:

```bash
meltano --environment=dev run tap-github target-sqlite
```

or:

```bash
export MELTANO_ENVIRONMENT=dev
meltano run tap-github target-sqlite
```

Once activated, plugins/processes can access the current environment via the `MELTANO_ENVIRONMENT` environment variable (empty string if none active).

**Default environments:** set `default_environment: <ENV>` in `meltano.yml` to avoid passing the flag every time. This does not apply to `meltano config`, which is for configuration, not execution.

### Example

```console
$ meltano --environment=prod config target-snowflake
{
  "dbname": "prod",
  "warehouse": "prod_wh",
  "batch_size_rows": 100000
}

$ meltano --environment=dev config target-snowflake
{
  "dbname": "dev",
  "warehouse": "dev_wh",
  "batch_size_rows": 1000
}
```

---

## State Backends

Meltano tracks pipeline state (for incremental loading) as part of each run so data isn't lost or duplicated. State can be stored in Meltano's system database, or — for ephemeral environments or when a dedicated backend DB is undesirable — in remote cloud storage.

### Supported backends

- System Database (default)
- Local Filesystem
- Amazon AWS S3 (and S3-compatible providers)
- Azure Blob Storage
- Google Cloud Storage
- Snowflake (external package)

Meltano's flexible state backend architecture also supports storing state in any key-value-capable system (other data warehouses, PostgreSQL, MySQL, MongoDB, Redis, custom APIs) via a custom state backend implementation.

State backends require Meltano 2.10+ (upgrade with `meltano upgrade` if older).

### Installation

No extra work needed for the default system database or local filesystem. For cloud storage backends, install with an extra:

- `meltano[s3]` — AWS S3 (and S3-compatible providers, e.g. Backblaze B2)
- `meltano[azure]` — Azure Blob Storage
- `meltano[gcs]` — Google Cloud Storage

### Configuration

#### Default (system database)

Main setting: `state_backend.uri`, defaults to the keyword `systemdb`.

```bash
meltano config set meltano state_backend.uri <URI>
```
or in `meltano.yml`:
```yaml
state_backend:
    uri: <URI for desired state backend>
```

#### Local filesystem

Set `state_backend.uri` to `file://<absolute path>`:

```bash
meltano config set meltano state_backend.uri 'file:///${MELTANO_SYS_DIR_ROOT}/state'
```

(Single quotes prevent early expansion of the environment variable.) State is stored at `file:///${MELTANO_SYS_DIR_ROOT}/state/<state_id>/state.json`. Uses the locking strategy described below.

#### Azure Blob Storage

Set `state_backend.uri` to `azure://<container_name>/<prefix>`. Two auth approaches (Meltano tries `DefaultAzureCredential` first, falls back to connection string):

**`DefaultAzureCredential`** — provide the storage account URL via `state_backend.azure.storage_account_url`. For `ManagedIdentity`, also set `AZURE_CLIENT_ID`.

```shell
MELTANO_STATE_BACKEND_URI='azure://meltano-state'
MELTANO_STATE_BACKEND_AZURE_STORAGE_ACCOUNT_URL='https://mystorageaccount.blob.core.windows.net/'
AZURE_CLIENT_ID='28a00fb0-67ee-4d11-81f8-10157e07c84f'  # only if using ManagedIdentity
```
Benefit: no need to enable shared key access on the storage account.

**Connection string** — via `state_backend.azure.connection_string` setting or `AZURE_STORAGE_CONNECTION_STRING` env var.

```shell
MELTANO_STATE_BACKEND_URI='azure://meltano-state'
AZURE_STORAGE_CONNECTION_STRING='DefaultEndpointsProtocol=https;AccountName=mystorageaccount;AccountKey=gSAw....'
```

#### AWS S3

Set `state_backend.uri` to `s3://<bucket>/<prefix>`. Authenticate via:

- `state_backend.s3.aws_access_key_id` / `state_backend.s3.aws_secret_access_key` settings, or
- credentials embedded in the URI: `s3://<aws_access_key_id>:<aws_secret_access_key>@<bucket>/<prefix>`, or
- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` env vars, or
- the AWS credentials file.

**Endpoint URL** (for custom S3 endpoints) can be set via the shared AWS config `endpoint_url`, `AWS_ENDPOINT_URL`, `AWS_ENDPOINT_URL_S3`, or `state_backend.s3.endpoint_url`. `AWS_IGNORE_CONFIGURED_ENDPOINT_URLS` has no effect if `state_backend.s3.endpoint_url` is set.

**S3-compatible providers**: works against any S3-compatible service boto3 can talk to. Configure `state_backend.s3.endpoint_url` plus the provider's access key ID/secret.

Backblaze B2 example:
```yaml
state_backend:
  uri: s3://my-b2-bucket/state
  s3:
    aws_access_key_id: <B2 Application Key ID>
    aws_secret_access_key: <B2 Application Key>
    endpoint_url: https://s3.<region>.backblazeb2.com
```

#### Google Cloud Storage

Set `state_backend.uri` to `gs://<bucket>/<prefix>`. Authenticate via:

**JSON credentials string** (production-friendly, containers) — `state_backend.gcs.application_credentials_json`:
```yaml
state_backend:
  uri: gs://my-bucket/state
  gcs:
    application_credentials_json: |
      {
        "type": "service_account",
        "project_id": "my-project",
        ...
      }
```

**Credentials file path** — `state_backend.gcs.application_credentials_path`:
```yaml
state_backend:
  uri: gs://my-bucket/state
  gcs:
    application_credentials_path: /path/to/service-account-key.json
```
(The legacy `state_backend.gcs.application_credentials` setting still works but is deprecated.)

**Default authentication** — falls back to the `GOOGLE_APPLICATION_CREDENTIALS` env var if set.

#### Snowflake (external)

Available as a separate package: [`meltano-state-backend-snowflake`](https://github.com/meltano/meltano-state-backend-snowflake).

```bash
# uv
uv tool install --with meltano-state-backend-snowflake meltano

# pipx
pipx install meltano
pipx inject meltano 'meltano-state-backend-snowflake'
```

Set `state_backend.uri` to `snowflake://<user>:<password>@<account>/<database>/<schema>`. State is stored in two auto-created tables: `meltano_state` (state data) and `meltano_state_locks` (concurrency locks).

```bash
export MELTANO_STATE_BACKEND_URI='snowflake://my_user:my_password@my_account/my_database/my_schema'
```

Features: automatic table creation/management, database-level locking, JSON state via Snowflake's VARIANT type, flexible connection config (account, user, password, warehouse, database, schema, role).

### Locking

The `systemdb` backend relies on transactional database logic to prevent conflicts across concurrent runs. Other backends use Meltano's own simple locking mechanism, configurable via:

- `state_backend.lock_timeout_seconds` (default 10)
- `state_backend.lock_retry_seconds` (default 1)

When acquiring a lock for a `state_id`, Meltano checks for a lock file/marker with a UTC timestamp. If none exists, it creates one. If one exists and has expired (timestamp + `lock_timeout_seconds` is in the past), Meltano overwrites it. If not expired, Meltano waits `lock_retry_seconds` and retries.

### Migrating state

Use `meltano state get` and `meltano state set` to migrate between backends. Example: migrating from `systemdb` to S3 for job `dev:tap-github-to-target-jsonl`.

Check current backend:
```shell
$ meltano config list meltano | grep state_backend.uri
state_backend.uri [env: MELTANO_STATE_BACKEND_URI] current value: 'systemdb' (default)
```

Export current state to a local file:
```shell
$ meltano state get dev:tap-github-to-target-jsonl > dev:tap-github-to-target-jsonl.json
```

Reconfigure to the new backend:
```shell
$ meltano config set meltano state_backend.uri "s3://meltano/state"
$ meltano config set meltano state_backend.s3.aws_access_key_id <AWS_ACCESS_KEY_ID>
$ meltano config set meltano state_backend.s3.aws_secret_access_key <AWS_SECRET_ACCESS_KEY>
```

Set state in the new backend from the local file:
```shell
$ meltano state set dev:tap-github-to-target-jsonl --input-file dev:tap-github-to-target-jsonl.json
```
(Confirm the overwrite prompt with `y`.)

For multiple jobs, loop through `meltano state list` and use `--force` to skip confirmation:
```shell
for job_id in $(meltano state list); do meltano state get $job_id > $job_id-state.json; done
```

Filter by pattern:
```shell
for job_id in $(meltano state list --pattern 'dev:*'); do meltano state get $job_id > $job_id-state.json; done
```

Then reconfigure the backend and set state for each file:
```shell
for state_file in *-state.json; do meltano state set --force ${state_file%-state.json} --input-file $state_file; done
```

---

## Python Virtual Environments

A Python virtual environment (venv) lets a Python application access specific versions of the libraries it needs, isolated from other applications. In the Singer ecosystem, taps and targets can have conflicting dependencies — venvs prevent those conflicts from breaking your setup.

Meltano uses venvs for two purposes:

1. Installing Meltano itself
2. Installing plugins (taps, targets, transformers, etc.)

### Why this matters

Ideally you don't need to think about venvs — using `pipx` to install Meltano manages venv creation for you (see the Installation guide). But if you need to build a custom production pipeline or otherwise customize your setup, understanding venvs helps avoid dependency conflicts with your OS or other Python applications.

### Creating and using a venv manually

Create a directory for your venvs (recommended inside your Meltano project, e.g. `.venv/meltano/`):

```bash
python -m venv .venv/meltano/
```

Activate it and upgrade pip (pip should be upgraded every time you create a new venv, to avoid dependency issues):

```bash
source .venv/meltano/bin/activate
pip install --upgrade pip
```

A successfully activated venv adds a `(meltano)` indicator to your shell prompt. The venv stays active until the shell closes; a new shell requires re-activation. Deactivate with `deactivate`.

Install Meltano into the active venv:

```bash
pip install meltano
```

(Using `pipx` is still generally recommended over this manual approach.)

### How Meltano uses venvs internally

Running `meltano install` creates a `.meltano/` directory in the project, with subdirectories per plugin type (e.g. `extractors/`). Inside, each plugin gets its own directory containing its dedicated virtual environment — Meltano runs the equivalent of the manual venv-creation steps automatically for every plugin.
