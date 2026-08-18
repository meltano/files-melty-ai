# Settings

Complete reference for Meltano's built-in settings — names, types, environment variables, and defaults.

Meltano determines the value of a setting by first looking in the environment, then in the project's `.env` file, then in the `meltano.yml` project file, falling back to a default value if nothing was found.

Use `meltano config list meltano` to list all available settings with their names, environment variables, and current values.

Configuration that is not environment-specific or sensitive should be stored in `meltano.yml` and checked into version control. Sensitive values like passwords and tokens belong in the environment or `.env`.

`meltano config set meltano <setting> <value>` automatically stores configuration in `meltano.yml` or `.env` as appropriate. `meltano.yml` formatting (indentation, spacing) can be customized via Meltano's user YAML configuration.

If supported by the plugin type, its configuration can be tested using `meltano config <plugin> test`.

## Plugin settings

For plugin-specific settings, refer to the plugin's own documentation on Meltano Hub, or use `meltano config list <plugin>` to list its settings, environment variables, and current values.

### `python` (plugin-level)

The Python version to use for a plugin — a path, or an executable name found within `$PATH`. Set at add-time with `meltano add --python <python>`.

If unspecified, falls back to the top-level `python` setting, or the Python executable used to run Meltano (in a separate virtual environment).

Only applies when creating new virtual environments — to change an existing venv's Python version, delete it from `.meltano/` and re-run `meltano install`.

Only applies to base plugins (which have their own venv). Inherited plugins use their base plugin's venv/Python version.

```yaml
plugins:
  extractors:
  - name: tap-gitlab
    variant: meltanolabs
    python: /path/to/python3.10
  loaders:
  - name: target-postgres
    variant: meltanolabs
    python: python3.10 # if it's in your $PATH
```

## Your Meltano project

### `default_environment`

- Environment variable: `MELTANO_DEFAULT_ENVIRONMENT`
- Default: `dev`

The default environment used when none is explicitly specified.

```bash
meltano config set meltano default_environment prod
# or
export MELTANO_DEFAULT_ENVIRONMENT=prod
```

### `python` (project-level)

- Environment variable: `MELTANO_PYTHON`

The Python version to use for plugins — a path, or executable name in `$PATH`. If unspecified, uses the Python executable used to run Meltano (separate venv). Overridable per-plugin (see above).

Only applies when creating new virtual environments — delete and reinstall to change an existing plugin's Python version. Only applies to base plugins.

```yaml
python: /path/to/python3.10 # or just python3.10 if it's in your $PATH
plugins:
  extractors: ...
  loaders: ...
```

### `send_anonymous_usage_stats`

- Environment variable: `MELTANO_SEND_ANONYMOUS_USAGE_STATS`
- `meltano init` CLI option: `--no-usage-stats` (implies `false`)
- Default: `true`

Meltano shares anonymous usage data (via Snowplow) with the Meltano team to understand feature usage and inform development. Some of this data is shared back to the community via MeltanoHub for plugin usage insights.

If enabled, the `project_id` setting uniquely identifies your project — sent unchanged if it's a UUID, otherwise hashed and used to derive a UUID. This project ID is also sent when requesting available plugins from `hub_url`.

To send tracking data to a different Snowplow account, configure `snowplow.collector_endpoints`.

To disable tracking entirely:
- Pass `--no-usage-stats` to `meltano init` for a new project
- Set `send_anonymous_usage_stats: false` in an existing project
- Set `MELTANO_SEND_ANONYMOUS_USAGE_STATS=false` to disable across all projects

```bash
meltano config set meltano send_anonymous_usage_stats false
# or
export MELTANO_SEND_ANONYMOUS_USAGE_STATS=false
# or
meltano init --no-usage-stats demo-project
```

**Anonymization standards.** Sent in clear text: plugin names, plugin variant names, command names, execution context (OS version, Python version, project ID). Anonymized via one-way hashing: CLI args, plugin config. Never collected: settings values, secrets/credentials, contents of `meltano.yml`.

**Q&A:** One-way hashing produces the same output for the same input, is effectively impossible to reverse, and lets Meltano detect changes to a file/configuration (e.g. whether `meltano.yml` changed since last hash) without ever transmitting or being able to reconstruct the source value. Meltano hashes any field that could be used to compromise a project or user — freeform CLI args are never sent in clear text, and collected data is never sold, shared, or traded with third parties.

### `disable_tracking`

- Environment variable: `MELTANO_DISABLE_TRACKING`
- Default: `None`

Alternative way to disable tracking. Any truthy value disables all tracking functionality.

```bash
meltano config set meltano disable_tracking true
# or
export MELTANO_DISABLE_TRACKING=true
```

### `project_id`

- Environment variable: `MELTANO_PROJECT_ID`
- Default: `None`

Uniquely identifies your project if `send_anonymous_usage_stats` is enabled.

```bash
meltano config set meltano project_id '<unique identifier>'
# or
export MELTANO_PROJECT_ID='<unique identifier>'
```

### `database_uri`

- Environment variable: `MELTANO_DATABASE_URI`
- `meltano *` CLI option: `--database-uri`
- Default: `sqlite:///$MELTANO_SYS_DIR_ROOT/meltano.db`

Meltano stores metadata in a project-specific system database — by default a SQLite database at `.meltano/meltano.db`. Choose a different backend/config via `--database-uri` or `MELTANO_DATABASE_URI`. Must be a valid SQLAlchemy database URL.

> Internal database migrations use `ALTER TABLE table RENAME COLUMN oldname TO newname` starting with Meltano v2.2.0, so the minimum required SQLite version is 3.25.1. Check yours with `sqlite3 --version`.

**PostgreSQL:**
```bash
meltano config set meltano database_uri postgresql+psycopg://<username>:<password>@<host>:<port>/<database>
# or
export MELTANO_DATABASE_URI=postgresql+psycopg://<username>:<password>@<host>:<port>/<database>
# or
meltano run --database-uri=postgresql+psycopg://<username>:<password>@<host>:<port>/<database> ...
```

**SQL Server (MSSQL):**
```bash
meltano config set meltano database_uri mssql+pymssql://<username>:<password>@<host>:<port>/<database>
# or
export MELTANO_DATABASE_URI=mssql+pymssql://<username>:<password>@<host>:<port>/<database>
# or
meltano run --database-uri=mssql+pymssql://<username>:<password>@<host>:<port>/<database> ...
```

> Databases other than SQLite require installing Meltano with extra components.

**PostgreSQL privileges and requirements.** PostgreSQL 13+ recommended. The database user needs:

- Database-level: `CONNECT`, `CREATE` (for schema creation during init), `TEMPORARY` (temp tables)
- Schema-level (typically `public`): `CREATE`, `USAGE`
- Object-level: `SELECT`, `INSERT`, `UPDATE`, `DELETE` on all Meltano tables; `USAGE`, `SELECT` on all sequences

Setup:
```sql
-- Connect as a superuser or database owner
GRANT CONNECT, CREATE, TEMPORARY ON DATABASE your_database TO meltano_user;

GRANT CREATE, USAGE ON SCHEMA public TO meltano_user;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO meltano_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO meltano_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO meltano_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO meltano_user;
```

Tables Meltano creates automatically: `runs` (job execution history), `state` (incremental state), `plugin_settings` (plugin config), `alembic_version` (schema migration tracking).

Meltano uses Alembic for schema migrations, run automatically as needed — requires `ALTER TABLE` privileges on existing tables.

Security considerations: use a dedicated least-privilege database user; store credentials via environment variables or `.env`; enable SSL connections via `database_uri` params; audit access logs regularly.

**Targeting a PostgreSQL schema:** append `?options=-csearch_path%3D<schema>` to `database_uri`/`MELTANO_DATABASE_URI`. Multiple schemas can be listed comma-separated (`<schema>,<schema_two>`) and PostgreSQL tries them left to right. Defaults to `public` if unset.

```bash
postgresql+psycopg://<username>:<password>@<host>:<port>/<database>?options=-csearch_path%3D<schema>
```

### `database_max_retries`

- Environment variable: `MELTANO_DATABASE_MAX_RETRIES`
- Default: `3`

Maximum reconnection attempts if the initial database connection fails at startup. Only affects the initial attempt; subsequent disconnections are handled by SQLAlchemy.

```bash
meltano config set meltano database_max_retries 3
# or
export MELTANO_DATABASE_MAX_RETRIES=3
```

### `database_retry_timeout`

- Environment variable: `MELTANO_DATABASE_RETRY_TIMEOUT`
- Default: `5` (seconds)

Retry interval if the initial database connection fails at startup. Only affects the initial attempt.

```bash
meltano config set meltano database_retry_timeout 5
# or
export MELTANO_DATABASE_RETRY_TIMEOUT=5
```

### `project_readonly`

- Environment variable: `MELTANO_PROJECT_READONLY`
- Default: `false`

Indicates the project is deployed read-only, blocking modifications to project files through the CLI in this environment — specifically, adding plugins or pipeline schedules to `meltano.yml`, and modifying plugin configuration stored in `meltano.yml` or `.env`.

`meltano config set <plugin>` can still store configuration in the system database, but settings already set in the environment or `meltano.yml` take precedence and can't be overridden.

```bash
meltano config set meltano project_readonly true
# or
export MELTANO_PROJECT_READONLY=true
```

### `hub_api_root`

- Environment variable: `MELTANO_HUB_API_ROOT`
- Default: `None`

Root URL for the Hub API. If set, overrides `hub_url`.

```bash
meltano config set meltano hub_api_root "https://mysite.com/my-plugins"
meltano config set meltano hub_api_root false
# or
export MELTANO_HUB_API_ROOT="https://mysite.com/my-plugins"
export MELTANO_HUB_API_ROOT=false
```

### `hub_url`

- Environment variable: `MELTANO_HUB_URL`
- Default: `https://hub.meltano.com`

Where Meltano finds the Hub listing discoverable plugins. Used primarily by `meltano add` and `meltano lock`, and when a full plugin definition is needed but no lock artifact is found.

```bash
meltano config set meltano hub_url http://localhost:4000
# or
export MELTANO_HUB_URL=http://localhost:4000
```

### `hub_url_auth`

- Environment variable: `MELTANO_HUB_URL_AUTH`
- Default: `None`

Value of the `Authorization` header sent to `hub_url`. No header is applied if unset, or set to `false`/`null`/empty string.

```bash
meltano config set meltano hub_url_auth "Bearer $ACCESS_TOKEN"
meltano config set meltano hub_url_auth false
# or
export MELTANO_HUB_URL_AUTH="Bearer $ACCESS_TOKEN"
export MELTANO_HUB_URL_AUTH=false
```

### `auto_install`

- Environment variable: `MELTANO_AUTO_INSTALL`
- Default: `true`

Whether to auto-install required plugins on command invocation. A plugin is auto-installed when its venv doesn't exist yet or `pip_url` changed.

Applies to: `meltano add`, `meltano config <plugin> test`, `meltano select --list`, `meltano test`, `meltano invoke`, `meltano el`/`meltano elt`, `meltano run`.

```bash
meltano config set meltano auto_install true
meltano config set meltano auto_install false
# or
export MELTANO_AUTO_INSTALL=true
export MELTANO_AUTO_INSTALL=false
```

## `meltano` CLI

Settings modifying the CLI's own behavior.

### `cli.log_level`

- Environment variable: `MELTANO_CLI_LOG_LEVEL`
- CLI option: `--log-level`
- Options: `debug`, `info`, `warning`, `error`, `critical`, `disabled`
- Default: `info`

CLI logging granularity. Ignored if a local logging config is found. `disabled` fully suppresses logging output — useful for scripts parsing Meltano output or silent runs.

```bash
meltano config set meltano cli log_level debug
# or
export MELTANO_CLI_LOG_LEVEL=debug
# or
meltano --log-level=debug ...
```

### `cli.log_format`

- Environment variable: `MELTANO_CLI_LOG_FORMAT`
- CLI option: `--log-format`
- Options: `colored`, `uncolored`, `json`, `key_value`, `plain`
- Default: `colored`

Shortcut for log output format. Ignored if a local logging config is found.

```bash
meltano config set meltano cli log_format json
# or
export MELTANO_CLI_LOG_FORMAT=json
# or
meltano --log-format=json ...
```

### `cli.log_config`

- Environment variable: `MELTANO_CLI_LOG_CONFIG`
- CLI option: `--log-config`
- Default: `logging.yaml`

Path to a valid YAML-formatted Python logging dict config file, used if present. Supports `.yaml` and `.yml`.

```bash
meltano config set meltano cli log_config /path/to/logging.yaml
# or
export MELTANO_CLI_LOG_CONFIG=/path/to/logging.yaml
# or
meltano --log-config=/path/to/logging.yaml ...
```

Sample logging config:
```yaml
version: 1
disable_existing_loggers: false

formatters:
  default:
    format: "[%(asctime)s] [%(process)d|%(threadName)10s|%(name)s] [%(levelname)s] %(message)s"
  structured_plain:
    (): meltano.core.logging.console_log_formatter
    colors: False
  structured_colored:
    (): meltano.core.logging.console_log_formatter
    colors: True
  key_value:
    (): meltano.core.logging.key_value_formatter
    sort_keys: False
  json:
    (): meltano.core.logging.json_formatter

handlers:
  console:
    class: logging.StreamHandler
    level: DEBUG
    formatter: structured_colored
    stream: "ext://sys.stderr"
  file:
    class: logging.FileHandler
    level: INFO
    filename: /var/log/meltano.log
    formatter: json

root:
  level: DEBUG
  propagate: yes
  handlers: [console, file]
```

### `cli.cwd`

- CLI option: `--cwd`
- Default: current directory

Run Meltano as if started in a specified directory (must contain a valid `meltano.yml`).

```bash
meltano --cwd '/path/containing/meltano_yml'
```

## `meltano elt`

Settings for `meltano el`/`meltano elt`.

### `elt.buffer_size`

- Environment variable: `MELTANO_ELT_BUFFER_SIZE`
- Default: `104857600` (100MiB in bytes)

Size of the buffer between extractor and loader (Singer tap/target) that queues messages waiting to be processed. If the extractor outpaces the loader, the buffer fills and the extractor blocks until half the buffer is free again.

A single line of extractor output is limited to half the buffer size — with the 100MiB default, max message size is 50MiB.

```bash
meltano config set meltano elt.buffer_size 52428800 # 50MiB in bytes
# or
export MELTANO_ELT_BUFFER_SIZE=52428800
```

## State Backends

### `state_backend.uri`

- Environment variable: `MELTANO_STATE_BACKEND_URI`
- Default: `systemdb`

URI for the state backend where Meltano stores state.

```bash
meltano config set meltano state_backend.uri "s3://your_bucket/meltano/state"
# or
export MELTANO_STATE_BACKEND_URI="s3://your_bucket/meltano/state"
```

### `state_backend.lock_timeout_seconds`

- Environment variable: `MELTANO_STATE_BACKEND_LOCK_TIMEOUT_SECONDS`
- Default: `10`

Seconds a state ID lock is considered valid in a state backend.

```bash
meltano config set meltano state_backend.lock_timeout_seconds 720
# or
export MELTANO_STATE_BACKEND_LOCK_TIMEOUT_SECONDS=720
```

### `state_backend.lock_retry_seconds`

- Environment variable: `MELTANO_STATE_BACKEND_LOCK_RETRY_SECONDS`
- Default: `1`

Seconds Meltano waits when trying to access/modify state for a locked state ID.

```bash
meltano config set meltano state_backend.lock_retry_seconds 720
# or
export MELTANO_STATE_BACKEND_LOCK_RETRY_SECONDS=720
```

### Azure-specific settings

#### `state_backend.azure.storage_account_url`

- Environment variable: `MELTANO_STATE_BACKEND_AZURE_STORAGE_ACCOUNT_URL`
- Default: `None`

Sign in to Azure via the Azure CLI first. `storage_account_url` is used to fetch default Azure credentials from the host system.

> At least one of `state_backend.azure.storage_account_url` and `state_backend.azure.connection_string` must be set to use Azure Blob Storage as a state backend. If `storage_account_url` is unset, Meltano falls back to `connection_string`.

```bash
meltano config set meltano state_backend.azure.storage_account_url "https://<myStorageAccountName>.blob.core.windows.net"
# or
export MELTANO_STATE_BACKEND_AZURE_STORAGE_ACCOUNT_URL="https://<myStorageAccountName>.blob.core.windows.net"
```

#### `state_backend.azure.connection_string`

- Environment variable: `MELTANO_STATE_BACKEND_AZURE_CONNECTION_STRING`
- Default: `None`

The Azure connection string used to authenticate to Azure.

```bash
meltano config set meltano state_backend.azure.connection_string "DefaultEndpointsProtocol=https;AccountName=myAccountName;AccountKey=myAccountKey"
# or
export MELTANO_STATE_BACKEND_AZURE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=myAccountName;AccountKey=myAccountKey"
```

### S3-specific settings

#### `state_backend.s3.aws_access_key_id`

- Environment variable: `MELTANO_STATE_BACKEND_S3_AWS_ACCESS_KEY_ID`
- Default: `None`

AWS access key ID for authenticating to S3.

```bash
meltano config set meltano state_backend.s3.aws_access_key_id "someaccesskeyid"
# or
export MELTANO_STATE_BACKEND_S3_AWS_ACCESS_KEY_ID="someaccesskeyid"
```

#### `state_backend.s3.aws_secret_access_key`

- Environment variable: `MELTANO_STATE_BACKEND_S3_AWS_SECRET_ACCESS_KEY`
- Default: `None`

AWS secret access key for authenticating to S3.

```bash
meltano config set meltano state_backend.s3.aws_secret_access_key "somesecretaccesskey"
# or
export MELTANO_STATE_BACKEND_S3_AWS_SECRET_ACCESS_KEY="somesecretaccesskey"
```

#### `state_backend.s3.endpoint_url`

- Environment variable: `MELTANO_STATE_BACKEND_S3_ENDPOINT_URL`
- Default: `None`

Endpoint URL for S3-compatible storage not hosted by AWS (e.g. Minio).

```bash
meltano config set meltano state_backend.s3.endpoint_url "https://play.min.io:9000"
# or
export MELTANO_STATE_BACKEND_S3_ENDPOINT_URL="https://play.min.io:9000"
```

### GCS-specific settings

#### `state_backend.gcs.application_credentials_json`

- Environment variable: `MELTANO_STATE_BACKEND_GCS_APPLICATION_CREDENTIALS_JSON`
- Default: `None`

JSON string of service account credentials for Google Cloud Storage. Recommended for production, especially containerized environments.

```bash
meltano config set meltano state_backend.gcs.application_credentials_json '{
  "type": "service_account",
  "project_id": "my-project",
  "private_key_id": "...",
  "private_key": "...",
  "client_email": "...",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}'

# Or set from a file:
meltano config set meltano state_backend.gcs.application_credentials_json --from-file service-account-key.json

# or
export MELTANO_STATE_BACKEND_GCS_APPLICATION_CREDENTIALS_JSON='{"type":"service_account","project_id":"my-project",...}'
```

#### `state_backend.gcs.application_credentials_path`

- Environment variable: `MELTANO_STATE_BACKEND_GCS_APPLICATION_CREDENTIALS_PATH`
- Default: `None`

Path to the credential file used to authenticate to Google Cloud Storage.

```bash
meltano config set meltano state_backend.gcs.application_credentials_path "path/to/creds.json"
# or
export MELTANO_STATE_BACKEND_GCS_APPLICATION_CREDENTIALS_PATH="path/to/creds.json"
```

#### `state_backend.gcs.application_credentials` (deprecated)

- Environment variable: `MELTANO_STATE_BACKEND_GCS_APPLICATION_CREDENTIALS`
- Default: `None`

> Deprecated. Use `state_backend.gcs.application_credentials_path` instead.

Path to the credential file used to authenticate to Google Cloud Storage.

```bash
meltano config set meltano state_backend.gcs.application_credentials "path/to/creds.json"
# or
export MELTANO_STATE_BACKEND_GCS_APPLICATION_CREDENTIALS="path/to/creds.json"
```

## Virtual environments

### `venv.backend`

- Environment variable: `MELTANO_VENV_BACKEND`
- Options: `virtualenv`, `uv`
- Default: `uv`

```bash
meltano config set meltano venv.backend virtualenv
meltano install --clean
# or
MELTANO_VENV_BACKEND=virtualenv meltano install --clean
```

> After switching virtual environment backends, reinstall all plugins with `meltano install --clean`.

## Snowplow Tracking

### `snowplow.collector_endpoints`

- Environment variable: `MELTANO_SNOWPLOW_COLLECTOR_ENDPOINTS`
- Default: `["https://sp.meltano.com"]`

Snowplow collector endpoints used if `send_anonymous_usage_stats` is enabled. Events are sent to all listed collectors.

## Feature Flags

### `experimental`

- Environment variable: `MELTANO_EXPERIMENTAL`
- Default: `False`

Enables experimental features under development, which may change or be removed in future versions.

```bash
meltano config set meltano experimental true
# or
export MELTANO_EXPERIMENTAL=true
```

### `ff.strict_env_var_mode`

- Environment variable: `MELTANO_FF_STRICT_ENV_VAR_MODE`
- Default: `False`

Raises an exception if an environment variable used in the project's Meltano configuration is not set.

### `ff.plugin_locks_required`

- Environment variable: `MELTANO_FF_PLUGIN_LOCKS_REQUIRED`
- Default: `False`

When enabled, plugins use only lock files to determine settings, installation source, etc. (except during `meltano add` operations). `meltano run` fails if a lock file is missing for a plugin.
