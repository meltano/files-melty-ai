# Deployment and Operations

Containerization, production deployment, logging, analysis (Superset), advanced topics, custom state backends, and user YAML formatting configuration.

## Containerization (Docker)

Once you've set up a Meltano project and run some pipelines on your local machine, it's time to repeat this trick in production. Production deployment involves getting Meltano, your project, and all of its plugins onto a new environment one-by-one, but you can greatly simplify this (and prevent issues caused by inconsistencies between environments) by wrapping them all up into a project-specific Docker container image.

This image can then be used on any environment running Docker (or a compatible tool like Kubernetes) to directly run `meltano` commands in the context of your project, without needing to separately manage the installation of Meltano, your project's plugins, or any of their dependencies.

If you're storing your Meltano project in version control (GitLab, GitHub), you can set up a CI/CD pipeline to run every time a change is made, automatically building a new version of the image and pushing it to a container registry. The image can then be pulled from that registry onto any local or cloud environment where you'd like to run your project's pipelines.

To containerize your project, add the appropriate `Dockerfile` and `.dockerignore` files by adding the `docker` file bundle:

```bash
# For these examples to work, ensure that
# Docker has been installed
docker --version

# Add Docker files to your project
meltano add files files-docker

# Build Docker image containing
# Meltano, your project, and all of its plugins
docker build --tag meltano-demo-project:dev .
```

Files added include a `Dockerfile` inheriting `FROM` the public `meltano/meltano:latest` image on Docker Hub.

### Image Variants

Meltano provides two types of Docker images to suit different use cases:

**Full Images (Default)**
- **Tags**: `latest`, `v3.9.1`, `latest-python3.11`, etc.
- **Includes**: All database connectors (PostgreSQL, MSSQL), build tools, and system dependencies
- **Use when**: You need MSSQL connectivity, or require plugins with complex system dependencies

**Slim Images (Recommended)**
- **Tags**: `latest-slim`, `v3.9.1-slim`, `latest-python3.11-slim`, etc.
- **Includes**: Azure, GCS, PostgreSQL, and S3 connectors with minimal dependencies
- **Excludes**: MSSQL connectors, build tools (gcc, make, etc.)
- **Use when**: You primarily use cloud storage backends and PostgreSQL, and want faster downloads and smaller deployments

**Choosing the right image:**

Use slim images if you: primarily use cloud storage (S3, GCS, Azure Blob Storage); want faster container startup and deployment times; don't require MSSQL database connectivity; are using plugins that don't need compilation or complex system dependencies.

Use full images if you: need MSSQL database connectivity; use plugins requiring build tools or complex system dependencies; need the complete set of database connectors and system tools.

### Customizing the Base Image

Customize the base image by modifying the `Dockerfile` or overriding the `MELTANO_IMAGE` `--build-arg`:

- **Public mirror**: `your-company/meltano:latest`
- **Specific version**: `meltano/meltano:v3.9.1` or `meltano/meltano:v3.9.1-slim`
- **Python version**: `meltano/meltano:latest-python3.12` or `meltano/meltano:latest-python3.12-slim`

```bash
# Use slim image (recommended for most use cases)
docker build --build-arg MELTANO_IMAGE=meltano/meltano:latest-slim --tag my-project:dev .

# Use specific version with Python 3.11
docker build --build-arg MELTANO_IMAGE=meltano/meltano:v3.9.1-python3.11-slim --tag my-project:dev .

# Use full image for MSSQL support
docker build --build-arg MELTANO_IMAGE=meltano/meltano:latest --tag my-project:dev .
```

Meltano publishes release images to Docker Hub (`meltano/meltano`). Using an alternative public mirror, or creating a private one, can avoid issues during your Docker build stage relating to registry rate limits.

The built image's entrypoint is the `meltano` command, meaning you can provide `meltano` subcommands and arguments like `run ...` and `invoke airflow ...` directly to `docker run <image-name> ...` as trailing arguments:

```bash
# View Meltano version
docker run meltano-demo-project:dev --version

# Run gitlab-to-jsonl pipeline with
# mounted volume to exfiltrate target-jsonl output
docker run \
  --volume $(pwd)/output:/project/output \
  meltano-demo-project:dev \
  run tap-gitlab target-jsonl
```

### Docker Compose

To experiment with a production-grade setup of your containerized project using Docker Compose, add the appropriate `docker-compose.prod.yml` file by adding the `docker-compose` file bundle:

```bash
# For these examples to work, ensure that
# Docker Compose has been installed
docker compose --version

# Add Docker Compose files to your project
meltano add files files-docker-compose

# Start the `meltano-system-db` service in the background
docker compose -f docker-compose.prod.yml up -d
```

For more details, refer to the README contained in the file bundle.

### GitLab CI/CD

To continuously build your project's Docker image and push it to GitLab's built-in Container Registry, add the appropriate `.gitlab-ci.yml` and `.gitlab/ci/docker.gitlab-ci.yml` files by adding the `gitlab-ci` file bundle:

```bash
# For these examples to work, ensure that
# you have an account on GitLab.com or
# a self-hosted GitLab instance with
# GitLab CI/CD and Container Registry enabled

# Add GitLab CI/CD files to your project
meltano add files files-gitlab-ci

# Initialize Git repository, if you haven't already
git init

# Add and commit all files
git add -A
git commit -m "Set up Meltano project with Docker and GitLab CI"

# Push to GitLab, which will automatically create
# a new private project at the specified path
NAMESPACE="<your-gitlab-username-or-group>"
git push git@gitlab.com:$NAMESPACE/meltano-demo-project.git master
```

GitLab CI/CD will start building your project's dedicated Docker image, available at `registry.gitlab.com/$NAMESPACE/meltano-demo-project:latest` once the CI/CD pipeline completes.

## Deployment in Production

This section covers: getting your Meltano project onto the production environment, installing Meltano, installing your project's plugins, storing pipeline state/metadata, storing pipeline logs, managing environment-specific/sensitive configuration, and running your pipelines.

If you're containerizing your Meltano project, you can skip most of the manual steps below and refer primarily to the "Containerized Meltano project" subsections.

> **Managed hosting options**: Meltano Cloud has been shut down in favor of Arch. Consider running your Meltano pipelines using a managed Airflow service like Astronomer, Google Cloud Composer, or Amazon MWAA.

### Your Meltano project

#### Off of your local machine

Since a Meltano project is just a directory of text-based files, you can treat it like any other software development project and benefit from DataOps best practices such as version control, code review, and CI/CD.

Getting your project onto production starts with getting it off of your local machine and onto a (self-)hosted Git repository platform like GitLab or GitHub.

By default, your project comes with a `.gitignore` file to ensure environment-specific and potentially sensitive configuration stored inside the `.meltano` directory and `.env` file is not leaked accidentally. All other files are recommended to be checked into the repository and shared between all users and environments.

#### ...and onto the production environment

Once your project is in version control, getting it to production can take various shapes. Recommended: set up a CI/CD pipeline to run automatically whenever new changes are pushed to your repository's default branch, connecting with the production environment and either directly pushing project files or triggering a mechanism to pull the latest changes.

A simpler (temporary) approach: manually connect to the production environment and pull the repository, now and/or whenever changes are made.

#### Containerized Meltano project

If you're containerizing your project, your project-specific Docker image will already contain all of your project files.

### Installing Meltano

The most straightforward way to install Meltano onto a production environment is to use `uv` to install the `meltano` package from PyPI.

If you add `meltano` (or `meltano==<version>`) to your project's `requirements.txt`, you can choose to automatically run `uv pip install -r requirements.txt` on your production environment whenever your project is updated, ensuring you're always on the latest (or requested) version.

**Containerized project**: your project-specific Docker image will already contain a Meltano installation since it's built from the `meltano/meltano` base image.

### Installing plugins

Whenever you add a new plugin, it's installed into the `.meltano` directory automatically. Since this directory is in `.gitignore` by default, you need to explicitly run `meltano install` whenever you clone or pull an existing project from version control, to install (or update) all plugins specified in `meltano.yml`.

It's strongly recommended to automatically run `meltano install` on your production environment whenever your project is updated, to ensure you're always using the correct versions of plugins.

**Containerized project**: your project-specific Docker image will already contain all of your project's plugins since `meltano install` is a step in its build process.

### Storing metadata

Meltano stores various types of metadata in a project-specific system database, which by default is a SQLite database at `.meltano/meltano.db`. Like all files in `.meltano` (included in `.gitignore` by default), the system database is also environment-specific.

SQLite is great for local development and testing since it requires no external database, but it has limitations that make it inappropriate for production — it's a simple file that only supports one concurrent connection.

It's strongly recommended to use a PostgreSQL system database in production instead, configured using the `database_uri` setting.

**Containerized project**: you will _definitely_ want to use an external system database, since changes to `.meltano/meltano.db` would not be persisted outside the container.

### Storing logs

Meltano stores all output generated by `meltano run` and `meltano el` in `.meltano/logs/elt/{state_id}/{run_id}/elt.log`, where `state_id` refers to the value autogenerated by `run`, provided to `el` via `--state_id`, or the name of a scheduled pipeline, and `run_id` is an autogenerated UUID.

To store these logs elsewhere, symlink the `.meltano/logs` or `.meltano/logs/elt` directory to a location of your choice.

**Containerized project**: these logs will not be persisted outside the container running your pipelines unless you exfiltrate them by mounting a volume inside the container at `/project/.meltano/logs/elt`.

### Managing configuration

All of your project's configuration that is _not_ environment-specific or sensitive should be stored in `meltano.yml` and checked into version control.

Configuration that _is_ environment-specific or sensitive is most appropriately managed using environment variables. Meltano Environments can be used to better manage configuration between different deployment environments. How these are best administered depends on your deployment strategy and destination.

To store sensitive configuration in a secrets store, consider using the `chamber` CLI, which lets you store secrets in AWS Systems Manager Parameter Store, exported as environment variables when executing an arbitrary command like `meltano`.

**Containerized project**: manage sensitive configuration using the mechanism provided by your container runner, e.g. Docker Secrets or Kubernetes Secrets.

### Running pipelines

#### `meltano run`

If all of the above has been set up correctly, run a pipeline using `meltano run`, just like locally. You can run the command using any mechanism capable of running executables — `cron`, Airflow's `BashOperator`, or any of dozens of other orchestration tools.

#### Airflow orchestrator

If you've added Airflow to your project as an orchestrator utility, have it automatically run your project's scheduled pipelines by starting its scheduler using `meltano invoke airflow scheduler`. Similarly, start its web interface using `meltano invoke airflow webserver`.

Take into account Airflow's own Deployment in Production Best Practices. Specifically, configure Airflow to:

- **Use the `LocalExecutor`** instead of the `SequentialExecutor` default, by setting `core.executor` (or `AIRFLOW__CORE__EXECUTOR`) to `LocalExecutor`:

  ```bash
  export AIRFLOW__CORE__EXECUTOR=LocalExecutor
  ```

- **Use a PostgreSQL metadata database** instead of the SQLite default (sounds familiar?), by setting `core.sql_alchemy_conn` (or `AIRFLOW__CORE__SQL_ALCHEMY_CONN`) to a `postgresql://` URI:

  ```bash
  meltano config set airflow core.sql_alchemy_conn postgresql://<username>:<password>@<host>:<port>/<database>

  # or:
  export AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql://<username>:<password>@<host>:<port>/<database>
  ```

  For this to work, the `psycopg2` package needs to be installed alongside `apache-airflow`, by adding `psycopg2` to `airflow`'s `pip_url` in `meltano.yml` (e.g. `pip_url: psycopg2 apache-airflow`) and running `meltano install utility airflow`.

**Containerized project**: the built image's entrypoint is the `meltano` command, meaning you can provide `meltano` subcommands and arguments like `elt ...` and `invoke airflow ...` directly to `docker run <image-name> ...` as trailing arguments.

## Logging and Monitoring

### Logging

Quickly change the log format of CLI output with the `--log-format` global option:

```bash
meltano --log-format=json run my-job
```

### Viewing Job Logs

Meltano stores logs for all job runs in the `.meltano/logs` directory. Use the `meltano logs` command to view them without navigating the filesystem.

```bash
# List recent job runs
meltano logs list

# View the log for a specific run
meltano logs show <log_id>
```

The `logs` command supports `--tail` for partial logs and `--format json` for JSON output, among other options.

### Configuring Logging

Logging can be controlled in more detail via a standard YAML-formatted Python logging dict config file (configuration dictionary schema).

By default, Meltano looks for this in a `logging.yaml` file in the project root (`.yaml` and `.yml` both supported). Override this via the `MELTANO_CLI_LOG_CONFIG` environment variable or the `--log-config` CLI option, e.g. `meltano --log-config=my-prod-logging.yaml ...`.

A `logging.yaml` contains a few key sections:

- `formatters` — controls the output format of log messages (e.g. json)
- `handlers` — controls the output destination of log messages (e.g. the console)
- `root` — the root logger, effectively the default config for all loggers unless otherwise configured
- `loggers` — explicit control of specific module/class/etc. named loggers

Key points:

1. Different handlers can use different formats. Meltano ships with 4 formatters:
   - `meltano.core.logging.console_log_formatter` — renders lines for the console, with optional colorization. When colorization is enabled, tracebacks are formatted with `rich`. Supports `colors` (bool), `show_locals` (bool), `max_frames` (int, default: 2), `all_keys` (bool), and `include_keys` (set[str]) parameters. By default, only essential keys are displayed for cleaner output.
   - `meltano.core.logging.json_log_formatter` — renders lines in JSON format.
   - `meltano.core.logging.key_value` — renders lines in key=value format.
   - `meltano.core.logging.plain_formatter` — renders lines in plain text format.
2. **Console output filtering**: by default the console formatter displays only essential log keys for cleaner output. Default keys: base keys `timestamp`, `level`, `event`, `logger`, `logger_name`; plugin subprocess keys `string_id`; plugin structured logging keys `plugin_exception`, `metric_info`.

   Control this via `all_keys` and `include_keys` parameters. When both are specified, **`include_keys` takes precedence**:
   1. If `include_keys` is set (regardless of `all_keys`): shows default keys + specified keys
   2. If only `all_keys: true` is set: shows all keys
   3. If neither is set (default): shows only default keys
3. Different loggers can use different handlers and log at different levels.
4. All standard Python logging handlers are supported (rotating files, syslog, etc).
5. If a logging config file is found, it takes precedence over `--log-format` and `--log-level` CLI options.

Annotated example `logging.yaml`:

```yaml
version: 1
disable_existing_loggers: false

formatters:
  default: # use a format similar to default generic python logging format
    format: "[%(asctime)s] [%(process)d|%(threadName)10s|%(name)s] [%(levelname)s] %(message)s"
  structured_colored:
    (): meltano.core.logging.console_log_formatter
    colors: true
  structured_colored_all_keys: # log format with colored output showing all log keys
    (): meltano.core.logging.console_log_formatter
    colors: true
    all_keys: true # displays all log keys instead of just the default set
  structured_plain_no_locals: # log format for structured plain text logs without colored output and without local variables
    (): meltano.core.logging.console_log_formatter
    colors: false # also disables `rich` traceback formatting
    show_locals: false # disables local variable logging in tracebacks (which be very verbose and leak sensitive data)
  structured_locals: # log format for structured plain text logs WITH local variables
    (): meltano.core.logging.console_log_formatter
    colors: true # also enables traceback formatting with `rich`
    show_locals: true # enables local variable logging in tracebacks (can be very verbose and leak sensitive data)
    max_frames: 5 # maximum number of frames to show in tracebacks (default: 2)
  key_value: # log format for traditional key=value style logs
    (): meltano.core.logging.key_value_formatter
    sort_keys: false
  json: # log format for json formatted logs
    (): meltano.core.logging.json_formatter
    callsite_parameters: true # adds `pathname`, `lineno`, `func_name` and `process` to each log entry
    dict_tracebacks: false # removes the `exception` object that is added to each log entry
    show_locals: true # enables local variable logging in tracebacks

handlers:
  console: # log to the console (stderr) using structured_colored formatter, logging everything at DEBUG level and up
    class: logging.StreamHandler
    level: DEBUG
    formatter: structured_colored
    stream: "ext://sys.stderr"
  meltano_log: # log everything INFO and above to a file in the project root called meltano.log in json format
    class: logging.FileHandler
    level: INFO
    filename: meltano.log
    formatter: json
  my_warn_file_handler: # log everything WARNING and above to automatically rotating log file in key_value format
    class: logging.handlers.RotatingFileHandler
    level: WARN
    formatter: key_value
    filename: /tmp/meltano_warn.log
    maxBytes: 10485760
    backupCount: 20
    encoding: utf8

root:
  level: DEBUG # the root logger must always specify a level
  propagate: yes # propagate to child loggers
  handlers: [console, meltano_log, my_warn_file_handler] # by default use these three handlers

loggers:
  somespecific.module.logger: # if you want debug logs for a specific named logger or module
    level: DEBUG
    handlers: [console]
    propagate: no
  urllib3: # for example hide all urllib3 debug logs
    level: WARNING
    handlers: [console, meltano_log]
    propagate: no
```

For a detailed explanation of the file format, see the Python logging documentation.

### Handling non-Unicode characters in plugin logs

On Windows, the default console encoding (e.g. `cp1252`) cannot represent all Unicode characters. When a plugin emits log lines containing non-ASCII text (e.g. Cyrillic or CJK characters), the standard `logging.StreamHandler` raises a `UnicodeEncodeError` and drops the log entry entirely.

Meltano ships a `SafeStreamHandler` that catches these errors and falls back to `backslashreplace` encoding, so unencodable characters are escaped instead of causing a crash or silent data loss. For example, the Cyrillic word `сам` would be written as `сам`.

This handler is **not used by default**. To opt in, reference it by its fully-qualified class name in a custom `logging.yaml` and point Meltano at that file via `cli.log_config` (or `--log-config` / `MELTANO_CLI_LOG_CONFIG`):

```yaml
version: 1
disable_existing_loggers: false

formatters:
  structured_colored:
    (): meltano.core.logging.console_log_formatter
    colors: true

handlers:
  console:
    class: meltano.core.logging.utils.SafeStreamHandler
    level: INFO
    formatter: structured_colored
    stream: "ext://sys.stderr"

root:
  level: INFO
  propagate: yes
  handlers: [console]
```

The only change relative to a standard config is replacing `class: logging.StreamHandler` with `class: meltano.core.logging.utils.SafeStreamHandler`. All other handler options (formatters, levels, streams) work identically.

### Local development config example

For terse console logging with DEBUG-level info still written to a log file behind the scenes:

```yaml
version: 1
disable_existing_loggers: false

formatters:
  structured_colored:
    (): meltano.core.logging.console_log_formatter
    colors: True
  json:
    (): meltano.core.logging.json_formatter

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: structured_colored
    stream: "ext://sys.stderr"
  file:
    class: logging.FileHandler
    level: DEBUG
    filename: meltano.log
    formatter: json

root:
  level: DEBUG
  propagate: yes
  handlers: [console, file]
```

To be even more terse, use level `WARN` instead of `INFO`. For something like a successful `meltano run` invocation this would produce no output at all.

### A generic starting config for log management providers

Most logging management tools readily accept structured logs in JSON format. Configuring Meltano to log in JSON format is a good first step.

To log to a file called `meltano.log` in JSON format while also reporting WARNING lines and above on the console:

```yaml
version: 1
disable_existing_loggers: false

formatters:
  structured_plain:
    (): meltano.core.logging.console_log_formatter
    colors: False
  json:
    (): meltano.core.logging.json_formatter

handlers:
  console:
    class: logging.StreamHandler
    level: WARNING
    formatter: structured_plain
    stream: "ext://sys.stderr"
  file:
    class: logging.FileHandler
    level: INFO
    filename: meltano.log
    formatter: json

root:
  level: DEBUG
  propagate: yes
  handlers: [console, file]
```

If instead you want console output in JSON format because your logging solution captures output directly:

```yaml
version: 1
disable_existing_loggers: false

formatters:
  json:
    (): meltano.core.logging.json_formatter

handlers:
  console:
    class: logging.StreamHandler
    formatter: json
    stream: "ext://sys.stderr"

root:
  level: INFO
  propagate: yes
  handlers: [console]
```

### Datadog logging config

The easiest approach: log to a file in JSON format and collect it with the Datadog Agent, using a `logging.yaml` config that writes directly to a file:

```yaml
version: 1
disable_existing_loggers: false

formatters:
  structured_plain:
    (): meltano.core.logging.console_log_formatter
    colors: False
  json:
    (): meltano.core.logging.json_formatter

handlers:
  console:
    class: logging.StreamHandler
    level: WARNING
    formatter: structured_plain
    stream: "ext://sys.stderr"
  file:
    class: logging.FileHandler
    level: INFO
    filename: meltano.log
    formatter: json

root:
  level: DEBUG
  propagate: yes
  handlers: [console, file]
```

With a Datadog Agent `conf.yaml` similar to:

```yaml
init_config:

instances:

##Log section
logs:
  - type: file
    path: "<PATH_TO_MELTANO>.log"
    service: "meltano"
    source: python
    sourcecategory: sourcecode
```

See Datadog's Python log collection docs for further details.

### Google Cloud logging config

The default `json_formatter` emits log lines using the structlog keys `event`, `level`, and `timestamp`. Google Cloud Logging (formerly Stackdriver) recognizes a JSON line as a structured entry only when it contains the special fields `severity`, `message`, and `timestamp`. As a result, logs produced by `json_formatter` are ingested as plain text at `INFO` severity, and severity-based filtering and alerting are unavailable.

To produce logs Google Cloud Logging parses correctly, set the `json_formatter` `preset` option to `google-cloud-logging`. The preset renames `event` to `message` and `level` to `severity`, allowing Cloud Logging to assign the appropriate severity. Suitable when Cloud Logging captures `stdout`/`stderr` directly, such as on Cloud Run or GKE, when running `meltano run`, `meltano invoke`, or `meltano el`:

```yaml
version: 1
disable_existing_loggers: false

formatters:
  google_cloud:
    (): meltano.core.logging.json_formatter
    preset: google-cloud-logging

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: google_cloud
    stream: "ext://sys.stderr"

root:
  level: INFO
  propagate: yes
  handlers: [console]
```

To include the source location of each log entry, enable callsite parameters. The preset then adds a `logging.googleapis.com/sourceLocation` field containing the file, line, and function:

```yaml
formatters:
  google_cloud:
    (): meltano.core.logging.json_formatter
    preset: google-cloud-logging
    callsite_parameters: true
```

### Log fields

Common fields useful for filtering or grouping:

- `level` — the log level.
- `timestamp` — the timestamp of the log entry.
- `event` — the actual log message.
- `name` or `source` — where the log message originated, e.g. `tap-gitlab` if it originated from a tap.
- `stdio` — when the log message originated from a plugin, indicates whether it came from stdout or stderr (filter out standard Singer events, for example).
- `cmd_type` — the type of command that the log message originated from.
- `state_id` — the associated state id.
- `success` — whether something succeeded or failed.
- `error` — where possible, the error type if one occurred.

### Tips and tricks

**Filter logs** using `jq` to only show lines you're interested in:

```bash
cat meltano.log | jq -c 'select(.string_id == "tap-gitlab" and .stdio == "stderr") | .event'
```

**Exclude plugin stdout logs**: when DEBUG level logging is enabled, a plugin's stdout logs can be very verbose (for extractors, this includes raw Singer messages). To exclude them, set the `meltano.plugins` logger to `INFO`:

```yaml
version: 1
disable_existing_loggers: no

loggers:
  # Disable logging of tap and target stdout
  meltano.plugins.stdout:
    level: INFO
    propagate: no
  root:
    level: DEBUG
    handlers: [console]
```

### Structured Log Parsing

Meltano includes advanced log parsing capabilities that automatically parse and re-emit structured logs from plugins, particularly those using the Singer SDK's structured logging format.

When plugins output structured JSON logs, Meltano can:

1. **Parse** the structured logs to extract semantic information
2. **Transform** the logs using the parsed data for enhanced metadata
3. **Re-emit** the logs through Meltano's logging system with additional context

This provides better log aggregation, filtering, and analysis while maintaining backward compatibility with existing logging infrastructure.

#### Supported Log Formats

**Singer SDK Structured Logs**: Meltano automatically detects and parses Singer SDK structured logs with these required fields:

- `level` — log level (debug, info, warning, error, critical)
- `pid` — process ID
- `logger_name` — name of the logger that emitted the log
- `ts` — timestamp (Unix timestamp)
- `thread_name` — thread name
- `app_name` — application name (e.g., "tap-github", "target-postgres")
- `stream_name` — stream name (if applicable)
- `message` — log message
- `extra` — additional metadata

Example:

```json
{
  "level": "info",
  "pid": 12345,
  "logger_name": "tap_github",
  "ts": 1705709074.883021,
  "thread_name": "MainThread",
  "app_name": "tap-github",
  "stream_name": "users",
  "message": "Processing stream users",
  "extra": {
    "record_count": 150,
    "api_endpoint": "https://api.github.com/users"
  }
}
```

**Metric Logs**: structured logs with metric information are handled specially:

```json
{
  "level": "info",
  "pid": 12345,
  "logger_name": "tap_github",
  "ts": 1705709074.883021,
  "thread_name": "MainThread",
  "app_name": "tap-github",
  "stream_name": "users",
  "message": "METRIC",
  "metric_info": {
    "metric_name": "records_processed",
    "value": 150,
    "tags": {"stream": "users", "status": "success"}
  },
  "extra": {}
}
```

#### Configuration

Log parsing is automatically enabled when Meltano detects that a plugin supports structured logging, controllable via plugin capabilities:

```yaml
plugins:
  extractors:
  - name: tap-github
    variant: meltanolabs
    capabilities:
    - structured-logs
```

Manually specify which parser to use for specific plugins:

```yaml
plugins:
  extractors:
  - name: tap-github
    variant: meltanolabs
    settings:
      log_parser: singer-sdk  # Force use of Singer SDK parser
```

#### Benefits

Structured log parsing enables enhanced metadata extraction, better filtering and search through tools like `jq`, and automatic performance monitoring through parsed metric logs — improved observability while maintaining backward compatibility.

#### Parser Implementation

Meltano uses a factory pattern for log parsers:

1. **SingerSDKLogParser** — parses Singer SDK structured JSON logs
2. **PassthroughLogParser** — fallback for unstructured logs
3. **LogParserFactory** — manages parser selection and fallback logic

The parsing process: attempts to parse with the preferred parser (if specified), falls back to trying all registered parsers, uses passthrough parser as final fallback, and maintains original log content if parsing fails.

#### Troubleshooting

**Parser selection issues** — if logs aren't parsed correctly:

1. Check plugin capabilities: `meltano invoke <plugin> --print-capabilities`
2. Verify log format matches expected structure
3. Review parser selection logic in debug logs

**Performance considerations** — log parsing adds minimal overhead:

- Parsing performance: ~381K logs/second
- Memory usage: minimal additional allocation
- Fallback behavior: preserves original performance for unparsable logs

**Debug log parsing**:

```yaml
loggers:
  meltano.core.logging.parsers:
    level: DEBUG
```

This shows parsing attempts and failures for debugging purposes.

## Analyze Data with Superset

Once your data is cleaned up and ready for consumption, Meltano lets you easily install and configure Superset for BI. With Superset you can connect to most popular data warehouses and build Charts and Dashboards.

### Installing Superset

Requires Meltano 2.0+. From inside your project:

```bash
meltano add utility superset
```

If you run into trouble installing Superset, check the OS Dependencies section in the Superset documentation (the rest of that guide isn't relevant since Meltano manages the installation, initialization, and configuration).

### Configuring Superset

#### Additional dependencies

Superset doesn't ship bundled with database connectivity except SQLite. Install the required packages for the database you want to use as your metadata database, plus packages needed to connect to databases you want to access through Superset. Find the list of supported databases and PyPI packages in Superset's documentation.

1. Find the `superset` plugin definition in `meltano.yml`
2. Update `pip_url` to include the desired additional packages:

```yaml
utilities:
- name: superset
  variant: apache
  pip_url: apache-superset==1.5.0 snowflake-sqlalchemy
```

3. Re-install the plugin:

```bash
meltano install superset
```

#### Secret key

If running Superset for the first time in a new environment, generate a new SECRET_KEY:

```bash
meltano config set superset SECRET_KEY $(openssl rand -base64 42)
```

#### Admin user

```bash
meltano invoke superset:create-admin
# Equivalent to `superset fab create-admin`
```

#### Load examples

```bash
meltano invoke superset:load-examples
# Equivalent to `superset load_examples`
```

For more details and a full list of settings, see the Superset plugin page on MeltanoHub.

### Starting the Superset UI

```bash
meltano invoke superset:ui
```

Available by default at http://localhost:8088; the backend database is saved in `$MELTANO_PROJECT_ROOT/.meltano/utilities/superset/`.

### Using Superset

1. Connect to your data source
2. Import datasets
3. Create Charts and Dashboards
4. Explore data with Superset's SQL Lab

### Advanced Superset Configurations

For advanced configurations using a `superset_config.py` to override Meltano configurations, see the Superset plugin page on MeltanoHub.

## Advanced Topics

### Installing Optional Components

Most Meltano features are available without installing any additional packages. Some niche or environment-specific features require installing Python extras.

```bash
# uv
uv tool install --from "meltano[postgres]" meltano

# pipx
pipx install "meltano[postgres]"
```

#### System Database

Extras adding support for different system database types (also the default state backend):

- `mssql` — Microsoft SQL Server (uses `pymssql`)
- `postgres` — PostgreSQL, using the modern `psycopg` driver

> The `psycopg2` extra is supported, but the package won't receive any new features — use the `postgres` extra instead.

To use these system databases, Meltano must be installed with the matching optional component.

#### State backends

Extras adding support for other state backends:

- `s3` — AWS S3
- `gcs` — Google Cloud Storage
- `azure` — Azure Blob Storage

### Extension Developer Kit (EDK)

Meltano extensions are lightweight executables that let you integrate existing data tools with Meltano. Extensions allow adding pre/post-hooks to run before/after Meltano executes the application, and project scaffolding customized per plugin (previously accomplished via file bundles).

The Extension Developer Kit (EDK) makes it easier for developers to build Meltano extensions.

#### Meltano Plugin Types

Meltano traditionally assigned a plugin type to each plugin based on functionality, used to activate plugin-type-specific features (piping Singer taps and targets together, running dbt deps before each run, compiling and removing the Airflow config.cfg to avoid storing sensitive credentials). This caused challenges getting new features implemented and accepted across the user base, since only one implementation was allowed:

- extractor (Singer Taps, e.g. tap-github)
- loader (Singer Targets, e.g. target-snowflake)
- transformer (dbt Adapters, e.g. dbt-snowflake)
- utility (e.g. SqlFluff, Airflow, Dagster)

The new approach groups all non-EL plugins under the `utility` plugin type, leaving only:

- extractor
- loader
- utility — now also including plugins previously called transformers and orchestrators

The logic for non-EL plugin-specific features has been extracted out of the Meltano codebase into a Meltano extension, allowing the community to iterate on plugin features more quickly and develop many variants of wrapper logic with different features. The transformer and orchestrator plugin types are still supported for now but will eventually be phased out as utilities take over.

### Running Custom Scripts

In addition to building EDK-based Python utilities, Meltano allows running arbitrary scripts as utilities — useful for minor tasks that don't require additional dependencies (set up/tear down tasks prior to running EL, interfacing with external services, etc.).

To run a Python script at the root of your project, add a custom utility with a command referencing the script:

```yaml
utilities:
- name: my_script_util
  namespace: my_script_util
  commands:
    run_script:
      executable: python
      args: my_script.py
    run_another_script:
      executable: python
      args: my_other_script.py
```

Add it to `meltano.yml` as a utility, then run it like any other plugin command (no `install` needed for this utility):

```bash
meltano run my_script_util:run_script
meltano invoke my_script_util:run_another_script
```

Similarly for bash scripts:

```yaml
utilities:
- name: my_script_util
  namespace: my_script_util
  commands:
    ls_directory:
      executable: /bin/bash
      args: -c ls
    remove_directory:
      executable: /bin/bash
      args: -c "rm -rf target"
```

### Airbyte Connector Integration FAQ

This FAQ covers `tap-airbyte-wrapper`, a Singer tap enabling any Airbyte source to be used as a Meltano extractor.

**How do the Singer and Airbyte specifications relate?** Singer started in 2016 by Stitch Data, specifying a data transfer format allowing any number of systems (taps) to send data to any destinations (targets). Airbyte (2020) created their own spec, heavily inspired by Singer. There are differences, but the core of each is sending new-line delimited JSON from STDOUT of a tap to STDIN of a target.

**How does the integration work?** A community member wrote `tap-airbyte-wrapper` using the Meltano Singer SDK. This wrapper calls the Docker image for a given Airbyte Source and translates messages into Singer-compatible format, conformed to the Singer standard, then sent to any Singer target listed on MeltanoHub.

**Do I need an Airbyte UI or API instance?** No — this integration runs Airbyte Source Connectors directly within your Meltano project; no need to run the Airbyte UI or API.

**Does this support Airbyte destination connectors?** No, Airbyte destinations are not supported.

**Recommended install/use**: any connector listed on MeltanoHub maintained by `airbyte` can be installed via `meltano add extractor <tap>`.

**Limitations of running Airbyte-based connectors**: mainly around putting these connectors into production — see below.

**Can I put a Meltano project with Airbyte connectors into production?** Depends on deployment target. The main challenge: if using Docker to package/deploy, you need Docker-in-Docker since each Airbyte connector is itself a Docker image. AWS ECS does not support docker-in-docker, though a simple EC2 instance with Docker works. GitHub Codespaces support docker-in-docker with a devcontainer.json addition, and Meltano on GitHub Actions is also possible.

**How does this work with custom Airbyte CDK connectors?** Works with any dockerized Airbyte source. Configure as a custom plugin in `meltano.yml`, replacing `name` and the `airbyte_spec.image` value with your Docker image reference:

```yaml
 - name: tap-pokeapi # REPLACE THIS WITH YOUR CONNECTOR NAME
   variant: airbyte
   executable: tap-airbyte
   namespace: tap_airbyte
   pip_url: git+https://github.com/MeltanoLabs/tap-airbyte.git
   capabilities:
   - catalog
   - state
   - discover
   - about
   - stream-maps
   - schema-flattening
   settings:
   - description: Airbyte image to run
     kind: string
     label: Airbyte Spec Image
     name: airbyte_spec.image
     value: airbyte/source-pokeapi # REPLACE THIS WITH YOUR IMAGE NAME
   - description: Airbyte image tag
     kind: string
     label: Airbyte Spec Tag
     name: airbyte_spec.tag
     value: latest
   - [INSERT OTHER SETTINGS HERE]
```

**What features does this add to Airbyte connectors?** Stream maps to adjust data on the fly, multiple environments to override configuration, version control since everything is in `meltano.yml`. Also supports alternative state backends (AWS S3, Azure Blob Storage, Google Cloud Storage) instead of the system database or local filesystem. Because it's SDK-based, it also unlocks the `BATCH` message format for better throughput.

**Do I need to do anything different with state?** No — Meltano manages state as usual.

**Migrating an existing Airbyte pipeline?** Requires determining a strategy for handling incremental state and table structure, since the loader will differ. Two recommendations: (1) if your source allows quick backfill, do a full sync with the Meltano pipeline into the new format and switch downstream processes; (2) stop the Airbyte pipeline and have the Meltano pipeline start where it left off (e.g., writing to a different table), then use dbt to union both tables into a common format.

**How do I access local files from my Airbyte connector?** Airbyte connectors run inside Docker containers without automatic access to your local filesystem — use the `docker_mount` setting:

```yaml
   config:
     docker_mounts: [{"source": "/<YOUR_FULL_LOCAL_PATH>/", "target": "/local/", "type": "bind"}]
     airbyte_spec:
       image: airbyte/source-file
     airbyte_config:
       dataset_name: test_file
       format: csv
       url: /local/data/test.csv
```

**Performance vs raw Airbyte sources?** Testing showed less than a 5% drop in overall throughput compared to running the same source natively via Docker.

**Is this experimental?** No longer — after hundreds of successful invocations and production use cases (e.g. Harness), these plugins are out of the experimental phase.

## Custom State Backends

Meltano's state backend system is highly extensible, allowing you to store pipeline state in virtually any system that can be a key-value store — cloud data warehouses like Redshift and BigQuery, or modern data stores like PostgreSQL or MongoDB.

To create a custom state backend, implement the `StateStoreManager` interface and any settings required to configure the backend.

> Before building a custom state backend, check if one of the built-in state backends meets your needs. Meltano includes support for system databases, local filesystems, and major cloud storage providers.

```python
# my_state_manager/backend.py
from contextlib import contextmanager
from urllib.parse import urlparse

from meltano.core.error import MeltanoError
from meltano.core.setting_definition import SettingDefinition, SettingKind
from meltano.core.state_store.base import MeltanoState, StateStoreManager


USERNAME = SettingDefinition(
    key="username",
    label="Username",
    kind=SettingKind.STRING,
    description="The username to use when connecting to the custom state manager",
)

PASSWORD = SettingDefinition(
    key="password",
    label="Password",
    kind=SettingKind.STRING,
    sensitive=True,
    description="The password to use when connecting to the custom state manager",
)


class MyStateManagerError(MeltanoError):
    pass


class MyStateManager(StateStoreManager):
    """My Custom State Manager"""

    label: str = "My Custom State Manager"

    def __init__(
        self,
        uri: str,
        *,
        username: str | None = None,
        password: str | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.uri = uri

        # Parse the URI to extract the connection details
        # Expecting `msm://<host>/<database>`, e.g. `msm://localhost/meltano`
        parsed = urlparse(uri)
        self.host = parsed.hostname
        self.database = parsed.path.lstrip("/")

        self.username = username or parsed.username

        if not self.username:
            raise MyStateManagerError("Username is required")

        self.password = password or parsed.password

        if not self.password:
            raise MyStateManagerError("Password is required")

    def set(self, state: MeltanoState) -> None:
        # Implement the logic to store the state in your custom backend
        ...

    def get(self, state_id: str) -> MeltanoState | None:
        # Implement the logic to retrieve the state from your custom backend
        ...

    def delete(self, state_id: str) -> None:
        # Implement the logic to delete the state for a given state ID
        ...

    def get_state_ids(self, pattern: str | None = None) -> list[str]:
        # Implement the logic to retrieve the list of state IDs from
        # your custom backend, optionally filtered by a glob pattern
        ...

    @contextmanager
    def acquire_lock(self, state_id: str, *, retry_seconds: float = 1.0):
        # Implement the logic to acquire a lock for the given state ID.
        # This method should be a context manager that acquires the lock
        # and releases it when the context exits.
        yield

    def migrate(self) -> None:
        # Optionally implement migration logic for your custom backend.
        # This is called by `meltano upgrade` to perform any necessary
        # data migrations (e.g., fixing path prefixes, schema changes).
        # The default implementation is a no-op.
        ...
```

To let Meltano know about your custom state manager, add the following configuration to your `pyproject.toml`:

```toml
[project.entry-points."meltano.settings"]
my_state_manager_username = "my_state_manager.backend:USERNAME"
my_state_manager_password = "my_state_manager.backend:PASSWORD"

[project.entry-points."meltano.state_backends"]
# These keys should match the expected scheme for URIs of
# the given type. E.g., filesystem state backends have a
# file://<path>/<to>/<state directory> URI
msm = "my_state_manager.backend:MyStateManager"
```

Use your custom state manager by installing it alongside Meltano:

```bash
uv tool install --with git+https://github.com/your-username/my-state-manager.git meltano
```

## User YAML Configuration

Meltano allows users to customize YAML formatting preferences (indentation, spacing) via a separate user configuration file — see `usage.md` for the full reference (configuration file locations, format, available settings, and how to disable it via `MELTANO_DISABLE_USER_YAML_CONFIG`).
