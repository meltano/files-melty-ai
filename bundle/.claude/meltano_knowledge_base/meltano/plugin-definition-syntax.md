# Plugin Definition Syntax

YAML syntax for defining plugins contributed to Meltano Hub.

## `name`

Required. The name of the plugin. The tuple `(name, variant)` must be unique.

```yaml
name: airflow
```

## `variant`

Required. The name of the variant. New variants of existing plugins usually come from forks or re-implementations.

```yaml
variant: apache
```

## `namespace`

Required. Used to configure multiple plugins meant to work together.

```yaml
namespace: airflow
```

## `label`

A human-readable label for the plugin.

```yaml
label: Airflow
```

## `description`

A brief description of what the tool, API, or file is used for.

```yaml
description: Customer-relationship management & customer success platform
```

## `docs`

The URL of the plugin's documentation.

```yaml
docs: https://docs.meltano.com/guide/orchestration
```

## `repo`

The URL of the plugin's repository (GitHub, GitLab, etc.). For extensions wrapping another application, this should point to the wrapped application's repository, not the extension's.

```yaml
repo: https://github.com/apache/airflow
```

## `ext_repo`

The URL of the plugin's own extension repository.

```yaml
ext_repo: https://github.com/meltano/airflow-ext
```

## `executable`

The default executable to call when invoking plugin commands.

```yaml
executable: airflow_invoker
```

## `capabilities`

Array of capabilities the plugin supports.

```yaml
capabilities:
- catalog
- discover
- state
```

Capabilities vary by plugin type.

### Extractor capabilities

`catalog`, `properties`, `discover`, `state`, `about`, `stream-maps`, `activate-version`, `batch`, `test`, `log-based`, `schema-flattening`, `structured-logging`.

### Loader capabilities

`about`, `stream-maps`, `activate-version`, `batch`, `soft-delete`, `hard-delete`, `datatype-failsafe`, `schema-flattening`, `structured-logging`.

### Mapper capabilities

`about`, `stream-maps`, `structured-logging`.

### `catalog` capability

Declares support for stream/property selection using the `--catalog` CLI argument — a newer version of the `properties` capability. Taps should declare `properties` or `catalog`, not both.

### `properties` capability

Declares support for stream/property selection using the `--properties` CLI argument — an older version of the `catalog` capability. Taps should declare `properties` or `catalog`, not both.

### `discover` capability

Declares the plugin can run with `--discover` to generate a `catalog.json`. Used by Meltano with `catalog`/`properties` to customize the catalog and apply selection logic.

### `state` capability

Declares the plugin can perform incremental processing using `--state`. Must be declared to use incremental data replication.

### `about` capability

Declares support for `--about` (with `--format=json`) to print plugin metadata in a machine-readable format. Used by users and by Meltano/MeltanoHub to auto-detect behaviors and capabilities.

### `stream-maps` capability

For Singer connectors: declares support for inline transformations/mappings within a stream. See the Singer SDK Stream Maps documentation.

### `activate-version` capability

Declares support for the `ACTIVATE_VERSION` message type, indicating all records for a stream have been sent and any records not seen should be soft-deleted.

### `batch` capability

Declares support for batch processing of records for more efficient data transfer.

### `test` capability

Declares support for a `--test` CLI argument to test connectivity/configuration without a full sync.

### `log-based` capability

Extractors only. Declares support for log-based replication (e.g. database change data capture).

### `schema-flattening` capability

Declares support for schema flattening — flattening nested objects into separate columns.

### `structured-logging` capability

Declares the plugin outputs structured logs (typically JSON) that can be parsed/processed by Meltano.

### `soft-delete` capability

Loaders only. Declares support for soft-deleting records (marking as deleted without physical removal).

### `hard-delete` capability

Loaders only. Declares support for hard-deleting records (physical removal from the destination).

### `datatype-failsafe` capability

Loaders only. Declares failsafe handling for data type mismatches, allowing ingestion to continue despite unexpected data types.

## `pip_url`

A string with the plugin's `pip install` argument. Can point to multiple packages and include any pip install options.

```yaml
pip_url: apache-airflow==2.10.5 --constraint https://raw.githubusercontent.com/apache/airflow/constraints-2.10.5/constraints-${MELTANO__PYTHON_VERSION}.txt
```

## `python`

The Python version or path for this plugin: a version number (e.g. `3.11`), a path to an executable (e.g. `/usr/bin/python3.10`), or an executable name found in `$PATH` (e.g. `python3.11`).

If unspecified, uses the Python executable used to run Meltano (in a separate venv).

```yaml
python: "3.11"
```
```yaml
python: /usr/bin/python3.10
```

## `supported_python_versions`

Optional. Array of Python versions the plugin supports. Used by Meltano to auto-select a compatible Python version when the plugin isn't compatible with Meltano's own Python version.

```yaml
supported_python_versions:
- "3.10"
- "3.11"
- "3.12"
```

## `maintenance_status`

The maintenance status of the plugin. See the JSON schema (github.com/meltano/hub) for the current list of allowed values.

```yaml
maintenance_status: active  # allowed values: active, beta, development, inactive, deprecated, unknown
```

## `domain_url`

The URL of the plugin's domain.

```yaml
domain_url: https://ads.google.com
```

## `logo_url`

Path to the plugin's logo in the Meltano Hub repository.

```yaml
logo_url: /assets/logos/utilities/airflow.png
```

## `definition`

Markdown-formatted text defining what the plugin is and does.

```yaml
definition: is an [utilities](/concepts/plugins#utilities) that allows for workflows to be programmatically authored, scheduled, and monitored via Airflow.
```

## `settings_preamble`

Text displayed before the settings in Meltano Hub, Markdown format.

```yaml
settings_preamble: |
  Meltano [centralizes the configuration](https://docs.meltano.com/guide/configuration) of all of the plugins in your project, including Airflow's. This means that if the [Airflow documentation](https://airflow.apache.org/docs/apache-airflow/stable/howto/set-config.html) tells you to put something in `airflow.cfg`, you can use `meltano config`, `meltano.yml`, or environment variables instead, and get the benefits of Meltano features like [environments](https://docs.meltano.com/concepts/environments).

  Any setting you can add to `airflow.cfg` can be added to `meltano.yml`, manually or using `meltano config`. For example, `[core] executor = SequentialExecutor` becomes `meltano config set airflow core executor SequentialExecutor` on the CLI, or `core.executor: SequentialExecutor` in `meltano.yml`. Config sections indicated by `[section]` in `airflow.cfg` become nested dictionaries in `meltano.yml`.
```

## `next_steps`

Documentation for next steps after installing the plugin, Markdown format.

```yaml
next_steps: |
  1. Use the [meltano schedule](https://docs.meltano.com/reference/command-line-interface#schedule) command to create pipeline schedules in your project, to be run by Airflow.

  1. If you're running Airflow for the first time in a new environment, create an admin user:

     ```sh
     meltano invoke airflow:create-admin
     # This is equivalent to `airflow users create` with some arguments in the Airflow documentation
     ```

  1. Launch the Airflow UI and log in using the username/password you created:

     ```sh
     meltano invoke airflow:ui
     ```

     By default, the UI will be available at [`http://localhost:8080`](http://localhost:8080). You can change this using the `webserver.web_server_port` setting documented below.

  1. Start Scheduler or execute Airflow commands directly using the instructions in [the Meltano docs](https://docs.meltano.com/guide/orchestration#starting-the-airflow-scheduler).
```

## `usage`

Free text describing how to use the plugin, Markdown format.

```yaml
usage: |
  ## Troubleshooting

  ### Error: `pg_config executable not found` or `libpq-fe.h: No such file or directory`

  This error message indicates that the [`libpq`](https://www.postgresql.org/docs/current/libpq.html) dependency is missing.

  To resolve this, refer to the ["Dependencies" section](#dependencies) above.
```

## `keywords`

Array of arbitrary keywords for search/classification.

```yaml
keywords:
- api
- meltano_sdk
```

## `requires`

Other plugins this plugin depends on.

```yaml
requires:
  files:
  - name: files-airflow
    variant: meltano
```

### `requires.<plugin_type>[*].name`

See the `requires` section above.

### `requires.<plugin_type>[*].variant`

See the `requires` section above.

## `requires_meltano`

Optional. A version specifier for the Meltano version required by this plugin. If the running Meltano version doesn't satisfy this, Meltano exits with an error when invoking the plugin. Uses Python package version specifier syntax.

```yaml
# Require Meltano 3.0 or higher
requires_meltano: ">=3.0.0"

# Require Meltano 3.x (3.0 or higher, but less than 4.0)
requires_meltano: ">=3.0.0,<4.0.0"

# Require exactly Meltano 3.5.0
requires_meltano: "==3.5.0"

# Require Meltano 3.6 or higher, but less than 3.8
requires_meltano: ">=3.6.0,<3.8.0"
```

> This field should only appear in plugin lockfiles, not `meltano.yml` for Hub plugins. It's primarily used by the Hub to indicate version compatibility.

## `commands`

Commands available for this plugin.

```yaml
commands:
  create-admin:
    args: "users create --username admin --firstname FIRST_NAME --lastname LAST_NAME --role Admin --email admin@example.org"
    description: Create an admin user.
  ui:
    args: webserver
    description: Start the Airflow webserver.
```

### `commands.<command_name>.args`

Command line arguments for the command.

### `commands.<command_name>.description`

Friendly description of the command.

### `commands.<command_name>.executable`

Optionally overrides the plugin's default `executable` when running this command.

### `commands.<command_name>.container_spec`

The container specification for running the command.

```yaml
- name: dbt
  pip_url: dbt-core~=1.0.1 dbt-postgres~=1.0.1
  commands:
    compile:
      args: compile
      container_spec:
        command: compile
        image: ghcr.io/dbt-labs/dbt-postgres:latest
        env:
          DBT_PROFILES_DIR: /usr/app/profile/
        volumes:
        - "$MELTANO_PROJECT_ROOT/transform/:/usr/app/"
    docs-generate:
      args: docs generate
      container_spec:
        command: docs generate
        image: ghcr.io/dbt-labs/dbt-postgres:latest
        env:
          DBT_PROFILES_DIR: /usr/app/profile/
        volumes:
         - "$MELTANO_PROJECT_ROOT/transform/:/usr/app/"
    docs-serve:
      args: docs serve
      container_spec:
        command: docs serve --no-browser
        image: ghcr.io/dbt-labs/dbt-postgres:latest
        env:
          DBT_PROFILES_DIR: /usr/app/profile/
        volumes:
        - "$MELTANO_PROJECT_ROOT/transform/:/usr/app/"
        ports:
          "8080": "8080/tcp"
```

Use with `meltano invoke --containers` to run commands in a container.

#### `commands.<command_name>.container_spec.image`

The Docker image to use for the command.

#### `commands.<command_name>.container_spec.command`

The command to run in the container.

#### `commands.<command_name>.container_spec.entrypoint`

The container entrypoint to use for the command.

#### `commands.<command_name>.container_spec.ports`

Mapping of host ports to container ports.

#### `commands.<command_name>.container_spec.volumes`

An array of host volumes to mount in the container.

#### `commands.<command_name>.container_spec.env`

A mapping of environment variables to set in the container.

## `settings_group_validation`

An array of arrays listing the minimal valid group of settings required to use the connector. A common use case: which settings are required for different authorization methods.

Example for Redshift, with 3 authorization types:

```yaml
settings_group_validation:
- - host
  - port
  - user
  - password
  - dbname
  - s3_bucket
  - default_target_schema
  - aws_profile
- - host
  - port
  - user
  - password
  - dbname
  - s3_bucket
  - default_target_schema
  - aws_access_key_id
  - aws_secret_access_key
- - host
  - port
  - user
  - password
  - dbname
  - s3_bucket
  - default_target_schema
  - aws_session_token
```

## `settings`

Each plugin variant in Meltano Hub has a `settings` property, nesting a variable number of individual settings. Each setting has optional properties described below.

```yaml
settings:
- name: core.dags_folder
  label: DAGs Folder
  value: $MELTANO_PROJECT_ROOT/orchestrate/dags
  env: AIRFLOW__CORE__DAGS_FOLDER
- name: core.plugins_folder
  label: Plugins Folder
  value: $MELTANO_PROJECT_ROOT/orchestrate/plugins
  env: AIRFLOW__CORE__PLUGINS_FOLDER
```

### `settings[*].name`

Required. The setting's name.

```yaml
settings:
- name: setting_name
```

A period in a name separates nesting levels, so `auth.username` is passed to the plugin as:
```json
{ "auth": { "username": "..." } }
```

If the plugin expects a key literally containing a period, escape it with a backslash (the same escaping used by `select` rules):

```yaml
settings:
- name: s3\.endpoint_url
```

That's passed through as a single literal key:
```json
{ "s3.endpoint_url": "..." }
```

Quote the escaped name when referencing it in a shell so the backslash isn't consumed:
```bash
meltano config tap-example set 's3\.endpoint_url' http://localhost:9000
```

### `settings[*].aliases`

Optional. An array of alternative names usable in `meltano.yml` and `meltano config set`.

```yaml
plugins:
- name: target-rdbms
  settings:
  - name: dbname
    aliases:
    - database
    - database_name
```

This means, alongside the `TARGET_RDBMS_DBNAME` environment variable, `target-rdbms` also supports `TARGET_RDBMS_DATABASE` and `TARGET_RDBMS_DATABASE_NAME` for the same setting, and the `dbname` setting can be referenced via `database`/`database_name` in `meltano.yml`/`meltano config set`.

### `settings[*].description`

Optional. Inline contextual help for the setting.

```yaml
settings:
- name: setting_name
  description: |
    This is a setting description.
```

### `settings[*].documentation`

Optional. Link to external supplemental documentation.

```yaml
settings:
- name: setting_name
  documentation: https://docs.meltano.com/reference/configuration#setting_name
```

### `settings[*].env`

Meltano injects the setting's value into the plugin's runtime environment as this variable, in addition to the default `<PLUGIN_NAME>_<SETTING_NAME>` variable.

```yaml
settings:
- name: setting_name
  env: SOME_API_KEY
```

The plugin can then access the value via `SOME_API_KEY`.

### `settings[*].hidden`

Optional. Hides the setting.

```yaml
settings:
- name: setting_name
  hidden: true
```

### `settings[*].kind`

Optional. First-class input control type. Default `string`. Supported values:

- `string` — text string (default)
- `integer` — integer number
- `boolean` — true/false
- `decimal` — decimal number
- `date_iso8601` — ISO 8601 date
- `email` — email address
- `file` — file path
- `array` — array of values
- `object` — nested object
- `options` — selection from predefined options (use with `options`)

```yaml
settings:
- name: setting_name
  kind: integer
```

> `kind: hidden` is deprecated in favour of `hidden: true`. `kind: password` is deprecated in favour of `sensitive: true`.

> Starting with Meltano v3.7, `date_iso8601` settings can have relative date values, like `3 days ago`, `yesterday`, `last week`, etc.

### `settings[*].label`

Optional. Human-friendly display text for the setting name.

```yaml
settings:
- name: setting_name
  label: Setting Name
```

### `settings[*].placeholder`

Optional. The input's placeholder default.

### `settings[*].sensitive`

Optional. Marks a setting as sensitive (password, token, code).

```yaml
settings:
- name: setting_name
  kind: string
  sensitive: true
```

### `settings[*].tooltip`

Optional. Tooltip text shown in UIs that support tooltips.

```yaml
settings:
- name: setting_name
  tooltip: Here is some more info...
```

### `settings[*].value`

Optional. Default value for the setting.

```yaml
settings:
- name: setting_name
  value: default_value
```

### `settings[*].options`

Optional. Used with `kind: options` to define available choices — each option has a `label` (display) and `value` (actual config value).

```yaml
settings:
- name: output_format
  kind: options
  label: Output Format
  description: The format of the output file.
  options:
  - label: JSON
    value: json
  - label: CSV
    value: csv
  - label: Parquet
    value: parquet
```

### `settings[*].value_processor`

Optional. A pre-processor applied to the setting value before use. Used primarily with `kind: object` to transform keys.

Available processors: `nest_object` (convert flat period-delimited-key object to nested object), `upcase_string` (uppercase the value).

```yaml
settings:
- name: config
  kind: object
  value_processor: nest_object
```

### `settings[*].value_post_processor`

Optional. A post-processor applied after the setting value is resolved.

Available processors: `nest_object`, `upcase_string`, `stringify` (convert JSON object to string), `parse_date` (parse value as a date).

```yaml
settings:
- name: start_date
  kind: date_iso8601
  value_post_processor: parse_date
```

## `env`

Optional. Environment variables used when expanding environment variables in lower levels of the project's configuration, and when running the plugin. These can reference other environment variables from higher levels.

```yaml
env:
  ENV_VAR_NAME: env var value
  PATH: "${PATH}:${MELTANO_PROJECT_ROOT}/bin"
```

## Plugin Type-Specific Attributes

### Loader-specific attributes

#### `dialect`

Loaders only. The dialect name of the target database — lets transformers in the same pipeline determine the database type to connect to.

```yaml
dialect: postgres
```

### Mapper-specific attributes

#### `mappings`

Mappers only. An array of named mapping configurations that can be invoked, each with a `name` and `config` object.

```yaml
mappings:
- name: hash-emails
  config:
    stream_maps:
      users:
        email: fake("email")
- name: remove-pii
  config:
    stream_maps:
      users:
        __filter__: record["country"] == "US"
```

### Transform-specific attributes (dbt)

#### `vars`

dbt transform plugins only. Object of dbt model variables passed to dbt.

```yaml
vars:
  my_variable: my_value
  another_variable: 123
```

#### `package_name`

dbt transform plugins only. The name of the dbt package's internal dbt project (the `name` value in `dbt_project.yml`).

```yaml
package_name: my_dbt_project
```
