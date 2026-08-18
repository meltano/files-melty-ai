# Command Line Interface

Complete reference for the `meltano` CLI: managing projects, plugins, and EL(T) pipelines.

For command line documentation syntax conventions, the [docopt](http://docopt.org/) standard is a useful reference.

## Global Configuration

CLI options available for the top-level `meltano` command:

**Current working directory**
- `--cwd` — Path to a directory containing a `meltano.yml` project file. Meltano runs as if started within that directory.

**Logging**
- `--log-config` — Path to a logging configuration file.
- `--log-format` — Shortcut for setting the log format instead of using `--log-config`. See CLI output for available options.
- `--log-level` — Set the log level. Valid values: `debug`, `info`, `warning`, `error`, `critical`.

**DotEnv**
- `--env-file` — Path to a `.env` file to load environment variables from. Absolute or relative to the current working directory.

**Color output** (via environment variables, for all subcommands):
- `NO_COLOR` — Set to a truthy value (`1`, `TRUE`, `t`) to disable colored output. See no-color.org.
- `FORCE_COLOR` — Set to a truthy value to enable colored log output even when stderr isn't a TTY. Added in Meltano v4.3.0.
- If both are set truthy, `NO_COLOR` takes precedence.

**UTC timestamps in logs**
- `NO_UTC` — Set to a truthy value to disable UTC timestamps in logs and use local time instead.

### Auto-install behavior

For commands supporting `--install/--no-install/--only-install`:

- `--install`: Install subject plugins if not already installed.
- `--no-install`: Do not install, even if missing.
- `--only-install`: Only install, without running the command.

If no flag is provided, behavior is determined by the boolean `auto_install` setting (see settings-reference.md), falling back to `--install` or `--no-install`.

---

## `add`

Adds or updates plugins in your Meltano project. Idempotent — running on an existing plugin updates it instead of failing.

When adding a new plugin, Meltano will:
1. Look up the plugin definition on Meltano Hub.
2. Add it to `meltano.yml` under `plugins: <type>s:`.
3. Store the plugin definition lock file in `./plugins`.
4. If a valid `pip_url` is specified, install it via `meltano install <name>`, creating a dedicated virtual environment at `.meltano/<type>s/<name>/venv` and running `pip install <pip_url>` (unless `--no-install`).
5. If the plugin declares unsupported Python for your version, override with `--force-install`.

Running `add` on an existing plugin updates the plugin definition and lock file without overwriting user-defined configuration. Use `--no-update` to instead fail when the plugin already exists.

Plugins install serially (unlike `meltano install`) to avoid missing dependencies (e.g. a transform requires `dbt` first).

### How to use

```bash
# Plugin type auto-detected from name
meltano add <name>
meltano add tap-gitlab      # extractor
meltano add target-postgres # loader
meltano add dbt-postgres    # utility

# Ignore required Python version
meltano add tap-gitlab --force-install

# Explicit plugin type (disambiguation)
meltano add --plugin-type <type> <name>
meltano add --plugin-type extractor tap-gitlab
```

**Automatic plugin type detection:** names starting with `tap-` → extractors; `target-` → loaders; everything else → utilities. Override with `--plugin-type` if detection fails.

Without `--custom`, `--inherit-from`, or `--from-ref`, this adds the discoverable plugin using a shadowing plugin definition.

**Variants:**
```bash
meltano add <name> --variant <variant>
meltano add target-postgres --variant transferwise
meltano add --plugin-type loader target-postgres --variant transferwise
```

**Custom plugins:**
```bash
meltano add --custom <name>
meltano add --custom tap-covid-19
meltano add --custom --plugin-type extractor tap-covid-19

# Docker: mount project dir and enable interactive mode for STDIN prompts
docker run --interactive -v $(pwd):/project -w /project meltano/meltano add --custom tap-covid-19
```

**Inheriting from an existing plugin:**
```bash
meltano add <name> --inherit-from <existing-name>
meltano add tap-ga--client-foo --inherit-from tap-google-analytics
meltano add --plugin-type extractor tap-ga--client-foo --inherit-from tap-google-analytics
```

**From a plugin definition YAML file (URL or local path):**
```bash
meltano add --from-ref <ref> <name>
meltano add tap-shopify --from-ref https://raw.githubusercontent.com/meltano/hub/main/_data/meltano/extractors/tap-shopify/matatika.yml
meltano add tap-shopify --from-ref /path/to/my/meltano/project/tap-shopify--matatika.yml
meltano add tap-shopify --from-ref tap-shopify--matatika.yml   # relative path

# The plugin name/variant given as arguments is superseded by the ref file's contents
meltano add this-will-be-ignored --from-ref tap-shopify--matatika.yml
meltano add this-will-be-ignored --variant this-will-also-be-ignored --from-ref tap-shopify--matatika.yml
```

`--from-ref` lets you add a plugin before it's on Meltano Hub, or try a plugin definition published at a public URL. Meltano errors if the referenced definition is invalid or missing required properties (see plugin-definition-syntax.md).

**Updating:** `meltano add` again updates the lock file and `meltano.yml` entry without overwriting user config.

**Skip install:**
```bash
meltano add <name> --no-install
meltano add tap-shopify --no-install
```

**Python version per plugin:** plugins default to the Python version used to run Meltano, unless overridden by the top-level `python` setting or per-plugin `python` attribute.
```bash
meltano add <name> --python <Python version or path>
meltano add tap-github --python python3.12
```
Regardless of the Python used at plugin-add time, `tap-github` and inheriting plugins will use Python 3.12.

### Parameters

- `--custom`: Add a custom plugin (prompts for base plugin description metadata).
- `--inherit-from=<existing-name>`: Add a plugin inheriting from an existing/discoverable plugin.
- `--as=<new-name>`: `meltano add <type> <name> --as=<new-name>` ≡ `meltano add <type> <new-name> --inherit-from=<name>`.
- `--variant=<variant>`: Add a specific non-default variant.
- `--install/--no-install`: Whether to install after adding. See Auto-install behavior above.
- `--update/--no-update`: Whether to update an existing plugin (default `--update`).
- `--from-ref=<ref>`: Add from a URL or local path as a custom plugin.
- `--force-install`: Ignore required Python version.
- `--python`: Python version for the plugin.

### Using `add` with Environments

Does not run relative to a Meltano Environment. `--environment` and `default_environment` are ignored if set.

---

## `compile`

> The `compile` command is currently in beta and subject to change without corresponding semantic version updates.

Generally runs automatically as needed; manual use is for generating manifest files.

```bash
meltano compile
meltano --environment <environment name> compile
meltano --no-environment compile          # no-environment manifest only
meltano compile --directory /some/directory/path

meltano compile --indent 2    # 2 spaces instead of default 4
meltano compile --indent 0    # newlines only
meltano compile --indent -1   # remove all non-essential whitespace
```

Manifest files default to `${MELTANO_SYS_DIR_ROOT}/manifests` (default `${MELTANO_PROJECT_ROOT}/.meltano/manifests`).

**Sensitive values:** redacted as `(redacted)` by default. Use `--unsafe` to expose them; `--safe` reaffirms the default (no functional effect either way).
```bash
meltano compile --unsafe
```

### Using `compile` with Environments

Accepts `--environment`, but `default_environment` is ignored. Specifying an environment compiles only that environment's manifest. Omitting it compiles a manifest per environment, including `meltano-manifest.json` (the no-environment manifest). Use `--no-environment` to compile only `meltano-manifest.json`.

---

## `config`

> **Command structure changed in Meltano v4.** The subcommand now comes *before* the plugin name.
> - New: `meltano config list <plugin>`, `meltano config set <plugin> <setting> <value>`
> - Old: `meltano config <plugin> list`, `meltano config <plugin> set <setting> <value>`
>
> Viewing config now requires the explicit `print` subcommand: `meltano config print <plugin>` (old: `meltano config <plugin>`).

Manages configuration of Meltano itself, any plugin, and plugin extras.

Without explicit `--store`, `meltano config set <plugin>` stores the value in the most appropriate location:
- the system database, if the project is deployed read-only;
- the current location, if a setting's default has already been overwritten;
- `.env`, if sensitive or environment-specific (`sensitive: true` / `env_specific: true`);
- `meltano.yml` otherwise.

If supported by the plugin type, test configuration with `meltano config test <plugin>`.

### How to use

```bash
# List settings (by default: required, explicitly configured, and custom settings only)
meltano config list meltano
meltano config list <plugin>
meltano config list <plugin> --all          # include optional settings at defaults
meltano config list <plugin> --filter ssl   # substring search, case-insensitive, across all settings

meltano config print <plugin>               # view current configuration

meltano config set <plugin> <name> <value>

# Values parsed as JSON, falling back to plain string if invalid JSON
meltano config set <plugin> <name> <string>
meltano config set <plugin> <name> "<word> <word> ..."
meltano config set <plugin> <name> <json>
meltano config set <plugin> <name> '<json>'
meltano config set <plugin> <name> '"<string>"'
meltano config set <plugin> <name> <number>
meltano config set <plugin> <name> <true/false>
meltano config set <plugin> <name> '[<elem>, ...]'
meltano config set <plugin> <name> '{"<key>": <value>, ...}'

meltano config unset <plugin> <name>
meltano config reset <plugin>               # clear config, back to defaults

# Target a specific store
meltano config set <plugin> --store=meltano_yml <name> <value>
meltano config unset <plugin> --store=dotenv <name>
meltano config reset <plugin> --store=db

# Test configuration
meltano config test <plugin>
meltano config --no-install test <plugin>
```

### Testing plugin configuration

`meltano config test <plugin>` validates configuration via a connectivity test:

- **Extractors (taps)**: invokes the extractor and checks it can emit at least one RECORD or BATCH message.
- **Loaders (targets)**: sends test Singer messages (SCHEMA, RECORD, STATE, optionally ACTIVATE_VERSION) and verifies error-free processing. For loaders with the `activate-version` capability, an ACTIVATE_VERSION message is included automatically.

```bash
meltano config test tap-gitlab
meltano config test target-postgres
meltano config test --plugin-type=loader target-jsonl   # disambiguate
```

> **Loader testing side effect:** test data is written to your target system — a table/collection called `meltano_test_stream` with one test record. You may need to clean this up manually.

Disambiguating by type generally:
```bash
meltano config list --plugin-type=<type> <plugin>
meltano config set --plugin-type=<type> <plugin> <name> <value>
```

Avoiding `$` expansion in a config value:
```bash
meltano config set <plugin> <name> "@\$a"
meltano config set <plugin> <name> '@$a'
```

**Sensitive values:** redacted as `(redacted)` in output by default. Use `--unsafe` to expose, `--safe` to reaffirm default.
```bash
meltano config --safe <plugin>
meltano config --safe <plugin> list
meltano config list <plugin>

meltano config --unsafe <plugin>
meltano config --unsafe <plugin> list
meltano config --unsafe <plugin> set <sensitive-name> <sensitive-value>
meltano config --unsafe <plugin> set --interactive
```

### Nested properties

Set/unset by specifying a list of property names:
```bash
meltano config set <plugin> <property> <subproperty> <value>
meltano config set <plugin> <property> <deep> <nesting> <value>

meltano config unset <plugin> <property> <subproperty>
```
Resulting plugin config:
```json
{
  "<property>": {
    "<subproperty>": "<value>",
    "<deep>": { "<nesting>": "<value>" }
  }
}
```

**Dot separator:** `meltano config list <plugin>` always shows full config keys with `.` nesting:
```bash
meltano config list <plugin>
# => <property>.<subproperty>
# => <property>.<deep>.<nesting>
```
You can set with `.` too, but a list of names is preferred since it reflects nesting properly in `meltano.yml`:
```bash
meltano config set <plugin> <property> <deep> <nesting> <value>
# meltano.yml:
#  config:
#    <property>:
#      <deep>:
#        <nesting>: <value>

meltano config set <plugin> <property>.<deep>.<nesting> <value>
# meltano.yml:
#  config:
#    <property>.<deep>.<nesting>: <value>
```

### Using `config` with Environments

Accepts `--environment`, but `default_environment` is ignored — unlike `run`/`invoke`, `config` ignores any configured default environment so base configuration can be set before environment-specific overrides.

### Plugin extras

Extras are distinguished from regular settings with an underscore prefix (e.g. `_example_extra`) — and in env vars get an extra underscore (e.g. `TAP_EXAMPLE__EXAMPLE_EXTRA`).

By default `config print`/`config list` show only regular settings; pass `--extras` to view/list only extras. `meltano config reset <plugin>` resets both settings and extras.

```bash
meltano config list <plugin> --extras
meltano config list <plugin> --extras --all
meltano config list <plugin> --extras --filter <substring>

meltano config print <plugin> --extras

meltano config set <plugin> _<extra> <value>
meltano config unset <plugin> _<extra>
meltano config reset <plugin>   # resets settings AND extras
```

### Interactive config

```bash
meltano config set <plugin> --interactive
meltano --environment=prod config set <plugin> --interactive
meltano config set <plugin> --interactive --extras
meltano config set <plugin> --interactive --store=dotenv
```

### Reading a setting value from a file

`--from-file` reads a configuration value from a file or piped process — useful for multiline strings or generated values. Settings of kind `object`/`array` are deserialized accordingly. Special filename `-` reads STDIN.

```bash
meltano config set <plugin> <name> --from-file ./file.txt
uuidgen | meltano config set <plugin> <name> --from-file -
```
For `object`/`array` settings, file contents must be valid JSON.

### Sensitive configuration

Values for settings defined as `sensitive: true` are redacted in output of:
```bash
meltano config list <plugin>
meltano config set <name> <value>
meltano config set <plugin> --interactive
```

---

## `docs`

Opens the Meltano documentation site in the default browser.

---

## `el`

Runs an EL pipeline (Extract and Load) using a chosen extractor and loader.

Each EL run has a State ID used to store/look up incremental replication state in the system database. If not provided via `--state-id` or `MELTANO_STATE_ID`, extraction always starts from scratch and a one-off State ID is auto-generated from the current date/time.

Output is logged inside `.meltano/logs/elt/{state_id}/{run_id}/elt.log` (`run_id` is an auto-generated UUID per run).

> `meltano run` is the recommended way to run cross-plugin workflows composably.

### How to use

```bash
meltano el <extractor> <loader> [--state-id TEXT]
```

### Parameters

- `--state-id` — identifies related EL(T) runs for state storage/lookup.
- `--full-refresh` flag (or `MELTANO_RUN_FULL_REFRESH=1`) — full refresh, ignoring prior state.
- `--force` — force a new run even if one with the same State ID is already running (otherwise errors).
- `--catalog` — manually provide a catalog file for the extractor (alternative to on-the-fly generation). Equivalent to setting the `catalog` extractor extra.
- `--state` — manually provide a state file for the extractor (alternative to State ID lookup). Equivalent to the `state` extractor extra.
- `--state-strategy` — `auto`, `merge`, or `overwrite` (default `auto`).
- `--merge-state` — **deprecated**, use `--state-strategy=merge`.
- One or more `--select <entity>` / `--exclude <entity>` — stream-level filtering on top of configured property selections. Discover stream names with `meltano select --list --all <extractor>`. Unix shell-style wildcards supported. `--exclude` takes precedence. Equivalent to the `select_filter` extractor extra. These preserve existing property-level selections from the `select` extra — they don't change which properties within a stream are extracted.
- `--dump` — dump a generated file to STDOUT instead of running the pipeline. Supported values: `catalog`, `state`, `extractor-config`, `loader-config`. Redirect with `>`.
- `--install/--no-install/--only-install` — auto-install behavior (see above).
- `--run-id` — use a provided UUID for the run (useful for external workflow tracking); catalog is cached for executions with the same run ID.

### Examples

```bash
meltano el tap-gitlab target-postgres --state-id=gitlab-to-postgres
meltano el tap-gitlab target-postgres --state-id=gitlab-to-postgres --full-refresh

meltano el tap-gitlab target-postgres --catalog extract/tap-gitlab.catalog.json
meltano el tap-gitlab target-postgres --state extract/tap-gitlab.state.json

meltano el tap-gitlab target-postgres --select commits
meltano el tap-gitlab target-postgres --exclude project_members
meltano el tap-gitlab target-postgres --select commits issues --exclude archived_issues

meltano el tap-gitlab target-postgres --state-id=gitlab-to-postgres --dump=state > extract/tap-gitlab.state.json
```

### Using `el` with Environments

Accepts `--environment`; `default_environment` applies if `--environment` isn't given.

### Debugging

Set `cli.log_level` to `debug` via `MELTANO_CLI_LOG_LEVEL` or `--log-level`:
```bash
MELTANO_CLI_LOG_LEVEL=debug meltano el ...
meltano --log-level=debug el ...
```

Debug mode logs the arguments/environment used to invoke the Singer tap/target executables (and dbt), including paths to config/catalog/state files:
```bash
$ meltano --log-level=debug el tap-gitlab target-jsonl --state-id=gitlab-to-jsonl
meltano            | INFO Running extract & load...
meltano            | DEBUG Invoking: ['demo-project/.meltano/extractors/tap-gitlab/venv/bin/tap-gitlab', '--config', 'demo-project/.meltano/run/tap-gitlab/tap.config.json', '--state', 'demo-project/.meltano/run/tap-gitlab/state.json']
meltano            | DEBUG Invoking: ['demo-project/.meltano/loaders/target-jsonl/venv/bin/target-jsonl', '--config', 'demo-project/.meltano/run/target-jsonl/target.config.json']
```

Dumped file contents can also be redirected via `--dump`. All Singer messages output by tap/target are logged with `<plugin name> (out)` prefixes:
```bash
tap-gitlab         | INFO Starting sync
tap-gitlab (out)   | {"type": "SCHEMA", "stream": "projects", "schema": {"type": "object", "properties": {...}}, "key_properties": ["id"]}
tap-gitlab (out)   | {"type": "RECORD", "stream": "projects", "record": {"id": 7603319, "name": "Meltano", ...}, "time_extracted": "2020-08-05T21:30:22.988250Z"}
tap-gitlab (out)   | {"type": "STATE", "value": {"project_7603319": "2020-08-05T21:04:59.158000Z"}}
tap-gitlab         | INFO Sync complete
target-jsonl (out) | {"project_7603319": "2020-08-05T21:04:59.158000Z"}
meltano            | INFO Incremental state has been updated at 2020-08-05 21:30:26.669170.
meltano            | DEBUG Incremental state: {'project_7603319': '2020-08-05T21:04:59.158000Z'}
meltano            | INFO Extract & load complete!
```

---

## `elt`

> **Deprecated** in favor of `el`.

Identical to `el`, plus it also runs transformations.

```bash
meltano elt <extractor> <loader> [--transform={run,skip,only}] [--state-id TEXT]
```

All `el` parameters apply, plus:
- `--transform`: `run` (run transforms), `skip` (default), `only` (skip extract/load, only run transforms).

```bash
meltano elt tap-gitlab target-postgres --transform=run --state-id=gitlab-to-postgres
```

---

## `environment`

Manages Environments in a Meltano project.

```bash
meltano environment add <environment_name>
meltano environment remove <environment_name>
meltano environment list
```

Once configured, `--environment` or `MELTANO_ENVIRONMENT` can be used with: `config`, `el`, `invoke`, `job`, `run`, `schedule`, `select`, `state`, `test`.

If `default_environment` is set in `meltano.yml`, these commands (except `config`) use that environment unless `--environment` or `MELTANO_ENVIRONMENT` is provided. To use no environment despite a `default_environment` setting, pass `--environment=null` (or `--environment null`) or use `--no-environment`.

### Using `environment` with Environments

Does not run relative to an Environment. `--environment`/`default_environment` are ignored if set.

### Examples

```bash
meltano environment add prod
meltano environment list
meltano --environment=prod config target-postgres set batch_size_rows 50000
meltano environment remove prod
```

---

## `hub`

Interacts with the configured Meltano Hub instance (default `https://hub.meltano.com`; configurable via the `hub_url` setting).

```bash
meltano hub ping
```

### Using `environment` with Environments

Accepts `--environment`; `default_environment` applies if not provided explicitly.

---

## `init`

Creates a new Meltano project at the given directory path. If the directory doesn't exist, it's created; if it exists and is empty, it's used.

New project directory contains:
- `meltano.yml` project file (plugins, pipeline schedules)
- Stubs: `.gitignore`, `README.md`, `requirements.txt`
- Empty `extract`, `load`, `transform`, `notebook`, `orchestrate` directories

Anonymous usage statistics are enabled by default unless `--no-usage-stats`, `MELTANO_SEND_ANONYMOUS_USAGE_STATS` is disabled, or `send_anonymous_usage_stats: false` is set in `meltano.yml`.

### How to use

```bash
meltano init [project_directory] [--no-usage-stats] [--force]
```

**Positional arguments:** `project_directory` — directory path to create the project at; use `.` for the current directory.

**Options:**
- `--no-usage-stats` — disables `send_anonymous_usage_stats`.
- `--force` — overwrites any existing `meltano.yml`.

### Examples

```bash
meltano init
meltano init demo-project
meltano init demo-project --no-usage-stats

# Disable for every future project:
SHELLRC=~/.$(basename $SHELL)rc
echo "export MELTANO_SEND_ANONYMOUS_USAGE_STATS=0" >> $SHELLRC
meltano init demo-project # --no-usage-stats implied

meltano init .
```

### Using `init` with Environments

Does not run relative to an Environment. `--environment` is ignored if set.

---

## `install`

Installs project dependencies based on `meltano.yml`.

```bash
meltano install   # installs all plugins
```

Optionally provide a plugin type and/or specific plugin names.

**Meltano v4+ syntax:**
```bash
meltano install tap-github target-postgres          # by name, type auto-detected
meltano install --plugin-type=extractor tap-gitlab  # by type
```

**Legacy (pre-v4) syntax:**
```bash
meltano install - tap-github target-postgres
meltano install extractor tap-gitlab
meltano install <plugin_type> <plugin_name>
```

`--schedule` installs plugins for a particular schedule only — useful in CI or deployments that install before every run.

Subsequent `meltano install` calls upgrade a plugin to latest, if available. Use `--clean` to fully uninstall and reinstall.

Plugins install in parallel by default (parallelism = number of CPUs); control with `--parallelism` (`--parallelism=1` disables parallel install).

`--force` overrides declared unsupported Python version restrictions.

> Package installation logs are stored at `.meltano/logs/pip/{plugin_type}/{plugin_name}/pip.log` — useful for debugging install issues.

### How to Use

```bash
meltano install
meltano install tap-github target-postgres
meltano install tap-gitlab

meltano install --plugin-type=extractor tap-gitlab
meltano install --plugin-type=extractors            # all extractors
meltano install --plugin-type=extractor tap-gitlab tap-adwords

meltano install --schedule=<schedule_name>

meltano install --parallelism=16
meltano install --clean
meltano install --force
```

### Using `install` with Environments

Does not run relative to an Environment. `--environment`/`default_environment` are ignored if set.

---

## `invoke`

Invokes a plugin's executable with specified arguments.

```bash
meltano invoke <plugin> [PLUGIN_ARGS...]
meltano invoke --plugin-type=<type> <plugin> [PLUGIN_ARGS...]   # disambiguate
```

`--dump` dumps generated config/catalog file content to STDOUT instead of invoking:
> Dumping config/catalog may reveal sensitive values in your terminal.
```bash
meltano invoke --dump=config <plugin>
meltano invoke --dump=catalog <plugin>
meltano invoke --refresh-catalog <plugin>
meltano invoke --refresh-catalog --dump=catalog <plugin>
```

`--no-install` skips auto-install before invoking:
```bash
meltano invoke --no-install <plugin>
```

`--refresh-catalog` (Singer extractors) ignores any cached catalog and re-runs discovery before invoking in sync mode or dumping the catalog.

Dumped content can be redirected: `meltano invoke --dump=catalog <plugin> > state.json`.

### Using `invoke` with Environments

Accepts `--environment`; `default_environment` applies if not provided explicitly.

### Commands

Plugins can define commands — shortcuts for argument combinations — invoked as `meltano invoke <plugin>:<command>`:
```bash
meltano invoke dbt:seed
meltano invoke dbt:snapshot
meltano invoke dbt:seed --show --threads 5   # extra args appended
meltano invoke --list-commands dbt           # list supported commands
```

### Containerized commands

```bash
meltano invoke --containers dbt:compile
```

### Debugging plugin environment

```bash
meltano invoke --print-var <PLUGIN_ENVIRONMENT_VARIABLE_1> <PLUGIN_NAME>
meltano invoke --print-var <PLUGIN_ENVIRONMENT_VARIABLE_1> --print-var <PLUGIN_ENVIRONMENT_VARIABLE_2> <PLUGIN_NAME>
```

---

## `lock`

Creates lock files for non-custom plugins.

```bash
meltano lock                                    # all plugins
meltano lock --plugin-type=<type>               # by type
meltano lock <name> <name_two>                  # specific plugins
meltano lock <name> <name_two> --plugin-type=<type>
meltano lock --update                           # update lock file from Hub
```

### Using `lock` with Environments

Does not run relative to an Environment. `--environment`/`default_environment` are ignored if set.

---

## `logs`

Utilities for viewing job logs — the CLI equivalent of the "Job Log" modal in the Meltano UI.

### `list`

Shows a table of recent job runs: run ID, job name, status, timing, duration.

### `show`

`meltano logs show <log_id>` displays log content for a specific job run (identified by run UUID).

### How to use

```bash
meltano logs list                        # 10 by default
meltano logs list --limit 25
meltano logs list --format json

meltano logs show <log_id>
meltano logs show <log_id> --tail 50
meltano logs show <log_id> --format json
```

### Examples

```bash
meltano logs list
meltano logs show 550e8400-e29b-41d4-a716-446655440000
meltano logs show 550e8400-e29b-41d4-a716-446655440000 --tail 50
meltano logs list --format json
```

### Options

`list`: `--limit`/`-l` (default 10), `--format` (`text`|`json`)
`show`: `--tail`/`-n`, `--format` (`text`|`json`)

### Notes

- Log IDs are UUIDs uniquely identifying each job run.
- `list` shows runs most-recent-first.
- Status indicators: PASS (success), FAIL (failed), RUN (running).
- Files >2MB prompt for confirmation before displaying.
- Stored at `.meltano/logs/elt/<state_id>/<run_id>/elt.log`.

---

## `remove`

Removes one or more plugins from the project: from `meltano.yml`, from `.meltano/<plugin_type>/<plugin_name>`, from the `plugin_settings` table in the system database, and from `./plugins/<plugin type>/` lock files.

```bash
meltano remove <name>              # type auto-inferred
meltano remove <name> <name_two>
```

### Using `remove` with Environments

Does not run relative to an Environment. `--environment`/`default_environment` are ignored if set.

### Examples

```bash
meltano remove tap-gitlab
meltano remove target-postgres target-csv
```

---

## `run`

Runs a set of command blocks in series.

Command blocks are plugin names, e.g. `meltano run some_tap some_mapping some_target some_plugin:some_cmd`, run left-to-right; a failure in any block aborts the entire run.

Multiple blocks can chain or repeat; extractor/loader pairs auto-link for EL work. With an active environment, a State ID is auto-generated per extractor/loader pair (format `<environment_name>:<tap_name>-to-<target_name>(:<state_id_suffix>)`) so subsequent runs resume. Inline mapping names are *not* included in generated IDs.

If no environment is active, `meltano run` does not generate a State ID and does not track state.

Named jobs (see `job` below) can be executed alongside other commands.

### How to use

```bash
meltano run tap-gitlab target-postgres
meltano run tap-gitlab target-postgres dbt-postgres:clean dbt-postgres:test dbt-postgres:run
meltano run tap-gitlab target-postgres tap-salesforce target-mysql
meltano run tap-gitlab target-postgres dbt-postgres:run tap-postgres target-bigquery
meltano --environment=<ENVIRONMENT> run tap-gitlab target-postgres
meltano run tap-gitlab one-mapping another-mapping target-postgres
meltano run tap-gitlab target-postgres simple-job
meltano run --state-id-suffix=<STATE_ID_SUFFIX> tap-gitlab target-postgres
meltano run --refresh-catalog tap-salesforce target-postgres
meltano run --timeout 3600 tap-gitlab target-postgres
```

### Parameters

`run` runs incrementally and saves state by default.

- `--dry-run` — parse/validate/explain without executing (implicitly enables `--log-level=debug` for console handlers).
- `--no-state-update` — disable state saving. Env var: `MELTANO_RUN_NO_STATE_UPDATE`.
- `--full-refresh` — force full refresh, ignoring prior state (state is still updated after completion unless `--no-state-update` also given). Env var: `MELTANO_RUN_FULL_REFRESH`.
- `--force` — force a run even if a conflicting job with the same generated ID is in progress.
- `--state-id-suffix` — custom suffix for the generated state ID per EL pair. Env var: `MELTANO_RUN_STATE_ID_SUFFIX`.
- `--state-strategy` — `auto` (default), `merge`, `overwrite`. Env var: `MELTANO_RUN_STATE_STRATEGY`.
- `--merge-state` — **deprecated**, use `--state-strategy`.
- `--run-id` — provided UUID for the run. Env var: `MELTANO_RUN_ID`.
- `--refresh-catalog` — force catalog refresh, ignoring cache. Env var: `MELTANO_RUN_REFRESH_CATALOG`.
- `--timeout` — max duration in seconds; pipeline is gracefully terminated after. Env var: `MELTANO_RUN_TIMEOUT`.
- `--install/--no-install/--only-install` — auto-install behavior.

### Examples

```bash
# autogenerated ID: 'dev:tap-gitlab-to-target-postgres', then 'dev:tap-gitlab-to-target-mysql'
meltano --environment=dev run tap-gitlab hide-secrets target-postgres tap-salesforce target-mysql

meltano --environment=dev run --full-refresh tap-gitlab target-postgres tap-salesforce target-mysql ...
meltano --environment=dev run --force tap-gitlab target-postgres tap-salesforce target-mysql ...

# ID: 'dev:tap-gitlab-to-target-postgres:pipeline-alias'
meltano --environment=dev --state-id-suffix pipeline-alias run tap-gitlab hide-secrets target-postgres

meltano --environment=dev run --state-strategy=merge tap-gitlab target-postgres
meltano --environment=dev run --timeout 3600 tap-gitlab target-postgres

MELTANO_RUN_TIMEOUT=1800 meltano --environment=dev run tap-gitlab target-postgres
MELTANO_RUN_FORCE=1 meltano --environment=dev run tap-gitlab target-postgres
MELTANO_RUN_STATE_ID_SUFFIX=pipeline-alias meltano --environment=dev run tap-gitlab target-postgres
MELTANO_RUN_STATE_STRATEGY=merge meltano --environment=dev run tap-gitlab target-postgres
MELTANO_RUN_NO_STATE_UPDATE=1 meltano --environment=dev run tap-gitlab target-postgres
MELTANO_RUN_REFRESH_CATALOG=1 meltano --environment=dev run tap-salesforce target-postgres
MELTANO_RUN_ID=550e8400-e29b-41d4-a716-446655440000 meltano --environment=dev run tap-gitlab target-postgres
```

### Using `run` with Environments

`run` always requires an Environment, provided via `--environment` or `default_environment` in `meltano.yml`.

---

## `job`

Defines one or more sequences of tasks (a job), run sequentially. Run a named job via `meltano run <job_name>`, or schedule it via `meltano schedule`.

### How to use

```bash
# Single task
meltano job add <job_name> --tasks "<tap_name> <mapping_name> <target_name> <command>"

# Multiple tasks (YAML array; one task per element)
meltano job add <job_name> --tasks "[<tap_name> <target_name>, <command>, <tap2_name> <target2_name>, ...]"

# Update existing job
meltano job set <job_name> --tasks "<tap_name> <mapping_name> <target_name> <command>"
meltano job set <job_name> --tasks "[<tap_name> <target_name>, <command>, <tap2_name> <target2_name>, ...]"

meltano job list
meltano job list --format=json
meltano job list <job_name>
meltano job list <job_name> --format=json
meltano job remove <job_name>
```

### Tasks

A task follows the same format as `meltano run` arguments — any valid sequence of plugins/plugin commands. Valid forms:

1. Extractor directly followed by a loader: `tap-gitlab target-postgres`
2. Extractor + one or more mappers + loader: `tap-gitlab hide-gitlab-secrets target-postgres`
3. A plugin invocation with optional command: `dbt-postgres:run` or `custom_utility_plugin`
4. Any sequence of the above: `tap-gitlab hide-gitlab-secrets target-postgres dbt-postgres:run tap-zendesk target-csv`

Single-task jobs can be a single quoted argument:
```bash
meltano job add tap-gitlab-to-target-postgres --tasks "tap-gitlab target-postgres"
meltano job add tap-gitlab-to-target-postgres-processed --tasks "tap-gitlab hide-gitlab-secrets target-postgres dbt-postgres:run custom-utility-plugin"
```
Resulting `meltano.yml`:
```yaml
jobs:
  - name: tap-gitlab-to-target-postgres
    tasks:
      - tap-gitlab target-postgres
  - name: tap-gitlab-to-target-postgres-processed
    tasks:
      - tap-gitlab hide-gitlab-secrets target-postgres dbt-postgres:run custom-utility-plugin
```

When a job is scheduled and generates an Airflow DAG, each task becomes a single DAG task. Splitting into multiple tasks is useful when steps need independent retry/rerun behavior (e.g. long-running steps separated from short downstream steps).

Multi-task jobs require an array passed to `meltano job add`:
```bash
meltano job add tap-gitlab-to-target-postgres-processed-multiple-tasks --tasks "[tap-gitlab hide-gitlab-secrets target-postgres, dbt-postgres:run, custom-utility-plugin]"
```
Resulting `meltano.yml`:
```yaml
jobs:
  - name: tap-gitlab-to-target-postgres-processed-multiple-tasks
    tasks:
      - tap-gitlab hide-gitlab-secrets target-postgres
      - dbt-postgres:run
      - custom-utility-plugin
```

Scheduling the single-task version yields a 1-task DAG; scheduling the multi-task version yields a 3-task DAG:
```
task 1: "meltano run tap-gitlab hide-gitlab-secrets target-postgres"
task 2: "meltano run dbt-postgres:run" , depends on task 1
task 3: "meltano run custom-utility-plugin", depends on task 2
```

### Using `job` with Environments

Accepts `--environment`; `default_environment` is ignored.

### Examples

```bash
meltano job add simple-demo --tasks "[tap-gitlab hide-gitlab-secrets target-postgres, dbt-postgres:run, tap-gitlab target-csv]"
meltano job list simple-demo --format=json
meltano run simple-demo
meltano run simple-demo tap-mysql target-bigquery
meltano job remove simple-demo
```

---

## `schedule`

> An `orchestrator` plugin is required to use `meltano schedule`.

Defines EL or Job pipelines run by an orchestrator at regular intervals — added to `meltano.yml`. Schedule either jobs or legacy `meltano el` tasks.

Run a scheduled pipeline's underlying command one-off via `meltano schedule run <schedule_name>`; CLI options (e.g. `--select=<entity>`, `--dry-run`) pass through.

The generated State ID differs by schedule type:

- **Jobs**: auto-generated from environment/plugins/state-id-suffix, same as `meltano run`.
  ```yaml
  jobs:
  - name: salesforce-to-parquet
    tasks:
    - tap-salesforce target-parquet
  schedules:
  - name: salesforce-daily # State ID e.g. 'dev:tap-salesforce-to-target-parquet'
    interval: "0 12 * * *"
    job: salesforce-to-parquet
  ```
- **EL schedules**: State ID is the schedule name itself — state is shared across all runs of that schedule.
  ```yaml
  schedules:
  - name: salesforce-daily # State ID: 'salesforce-daily'
    interval: "@daily"
    extractor: tap-salesforce
    loader: target-parquet
  ```

### How to use

Interval is a cron expression or one of: `@hourly` (`0 * * * *`), `@daily` (`0 0 * * *`), `@weekly` (`0 0 * * 0`), `@monthly` (`0 0 1 * *`), `@yearly` (`0 0 1 1 *`), or `@manual`/`@once`/`@none` (aliases for manual-trigger-only schedules).

```bash
meltano schedule add <schedule_name> --job my_job --interval "@daily"
meltano schedule add <schedule_name> --extractor <tap> --loader <target> --interval "@hourly"

meltano schedule list [--format=json]
meltano schedule remove <schedule_name>

meltano schedule set <schedule_name> --interval <new-interval>
meltano schedule set <schedule_name> --job <new-job>
meltano schedule set <schedule_name> --extractor <new-tap> --interval <new-interval>

meltano schedule run <schedule_name>
```

### Using `schedule` with Environments

Accepts `--environment`; `default_environment` is ignored.

### Examples

```bash
meltano schedule add gitlab-sync --job gitlab-to-mysql --interval "@daily"

meltano schedule run gitlab-sync --dry-run   # runs `meltano run --dry-run gitlab-sync` internally

meltano schedule set gitlab-sync --job gitlab-to-postgres
meltano schedule set gitlab-sync --interval "@weekly"

meltano schedule add gitlab-to-jsonl --extractor tap-gitlab --loader target-jsonl --interval="* * * * *"
meltano schedule set gitlab-to-jsonl --loader target-csv
```

---

## `select`

Adds select patterns to a specific extractor in the project:

```
meltano select [--list] [--all] [--clear] <tap_name> [ENTITIES_PATTERN] [ATTRIBUTE_PATTERN]
```

Selection rules are stored in the extractor's `select` extra (streams/properties included during extraction) — distinct from the `select_filter` extra (used for further filtering stream selections at runtime).

> Not all taps support this. Taps need the `--discover` switch. Check with `meltano invoke tap-... --discover`.

### How to use

Unix shell-style wildcards in patterns:
- `*` — any sequence of characters
- `?` — one character
- `[abc]` — `a`, `b`, or `c`
- `[!abc]` — any character except `a`, `b`, `c`

`--list`/`--json` list currently selected attributes; `--all` shows all attributes with selected status. `--rm`/`--remove` removes previously added patterns. `--clear` removes all patterns, reverting to default behavior.

### Using `select` with Environments

Accepts `--environment`; `default_environment` is ignored.

### Examples

```bash
meltano select tap-gitlab --list --all
meltano select tap-gitlab --json --all

meltano select tap-gitlab tags "*"          # all attributes of an entity
meltano select tap-gitlab commits id        # specific attributes
meltano select tap-gitlab commits project_id
meltano select tap-gitlab commits created_at
meltano select tap-gitlab commits author_name
meltano select tap-gitlab commits message

# Nested properties
meltano select tap-gitlab users address
meltano select tap-gitlab users address city
meltano select tap-gitlab users address geo lat

# Note: these define what's available; to filter which streams are processed at runtime use:
# meltano el tap-gitlab target-jsonl --select commits tags

meltano select tap-gitlab --exclude "*" "*_url"   # exclude matching attributes of all entities

meltano select tap-gitlab --list
meltano select --no-install tap-gitlab --list
```

Example output:
```
Enabled patterns:
    tags.*
    commits.id
    commits.project_id
    commits.created_at
    commits.author_name
    commits.message
    users.address
    users.address.city
    users.address.geo.lat
    !*.*_url

Selected attributes:
    [selected ] commits.author_name
    [selected ] commits.created_at
    [automatic] commits.id
    [selected ] commits.message
    [selected ] commits.project_id
    [automatic] tags.commit_id
    [selected ] tags.message
    [automatic] tags.name
    [automatic] tags.project_id
    [selected ] tags.target
    [selected ] users.address
    [selected ] users.address.city
    [selected ] users.address.geo.lat
```

Remove patterns:
```bash
meltano select tap-gitlab --rm tags "*"
meltano select tap-gitlab --rm --exclude "*" "*_url"
meltano select tap-gitlab --rm commits id
```

Clear all patterns:
```bash
meltano select tap-gitlab --clear
```

> Most shells parse glob syntax — quote select patterns to escape special characters.

### Exclude parameter

`--exclude` excludes all matching attributes. `automatic` attributes are always included regardless of exclude patterns; only `available` attributes can be excluded. Exclusion takes precedence over inclusion — an excluded attribute can't be re-included without removing the exclusion pattern.

```bash
meltano select --exclude tap-carbon-intensity '*' 'longitude'
meltano select --exclude tap-carbon-intensity '*' 'latitude'
```
This excludes all `longitude` and `latitude` attributes.

---

## `state`

Manages Singer State for jobs via the CLI.

### `clear`

Clears state for a given `state_id`. Prompts for confirmation.
```bash
meltano state clear [--force] <state_id>
```
`--force` disables confirmation prompts (use with caution).
```bash
meltano state clear dev:tap-gitlab-to-target-jsonl
meltano state clear --force dev:tap-gitlab-to-target-jsonl
```

### `get`

Retrieves state for a given `state_id`.

> **Output format changed in v4:** default output changed from pretty-printed to compact single-line JSON, directly compatible with `meltano state set`. Use `--format=pretty` for the legacy pretty-printed behavior.

```bash
meltano state get <state_id>                  # compact (default in v4+)
meltano state get <state_id> --format=pretty  # human-readable
```

`--format` options: `json` (default, compact) or `pretty` (legacy v3 behavior).

```bash
meltano state get dev:tap-gitlab-to-target-jsonl
meltano state get dev:tap-gitlab-to-target-jsonl --format=pretty

# Round-trip copy between state IDs
meltano state get dev:tap-gitlab-to-target-jsonl | \
  meltano state set --force prod:tap-gitlab-to-target-jsonl "$(cat)"

meltano state get dev:tap-gitlab-to-target-jsonl > state-backup.json
meltano state set --force dev:tap-gitlab-to-target-jsonl --input-file state-backup.json
```

### `list`

Lists all `state_id`s in the system database.
```bash
meltano state list [--pattern] <PATTERN>
```
`--pattern` filters by wildcard (`*`). Note: shells auto-expand `*` — quote the pattern.
```bash
meltano state list
meltano state list 'dev:*'
meltano state list --pattern '*tap-gitlab*'
```

### `merge`

Merges new state onto existing state for a state ID.

> Merged state is computed at execution time. `merge` adds a new payload to the database, merged with existing payloads the next time state is read via `meltano el`, `meltano run`, or `meltano state get`.

```bash
meltano state merge <state_id> --input-file <file>
meltano state merge <state_id> <RAW STATE JSON>
meltano state merge <state_id> --from-state-id <src_state_id>
```
`--input-file` reads from a file; `--from-state-id` reads from an existing state ID. State must be provided in exactly one way.
```bash
meltano state merge dev:tap-gitlab-to-target-jsonl '{"singer_state": {"project_123456_issues": "2020-01-01"}}'

echo '{"singer_state": {"project_123456_issues": "2020-01-01"}}' > gitlab_state.json
meltano state merge dev:tap-gitlab-to-target-jsonl --input-file gitlab_state.json

meltano state merge dev:tap-gitlab-to-target-jsonl --from-state-id prod:tap-gitlab-to-target-jsonl
```

### `copy`

Copies state from one state ID to another.
```bash
meltano state copy <src_state_id> <dst_state_id>
meltano state copy prod:tap-gitlab-to-target-jsonl dev:tap-gitlab-to-target-jsonl
```

### `move`

Moves state from one state ID to another (rename).
```bash
meltano state move <src_state_id> <dst_state_id>
meltano state move original-tap-postgres-to-target-jsonl variant-tap-postgres-to-target-jsonl
```

### `set`

Sets state for a job. By default validates the state is valid Singer state with a top-level `singer_state` key.

```bash
meltano state set <state_id> --input-file <file>              # prompts + validates
meltano state set --force <state_id> --input-file <file>      # skip confirmation
meltano state set <state_id> <RAW STATE JSON>
meltano state set --force <state_id> <RAW STATE JSON>
meltano state set --force --no-validate <state_id> <RAW STATE JSON>   # skip validation, not recommended
```
`--input-file` reads state from a file; `--force` disables confirmation; `--no-validate` skips format validation (use only in edge cases needing non-standard state).

> By default validates: value is valid JSON, and contains a top-level `singer_state` key. Bypass with `--no-validate` (not recommended — invalid state can cause unexpected full refreshes).

```bash
meltano state set --force dev:tap-gitlab-to-target-jsonl '{"singer_state": {"project_123456_issues": "2020-01-01"}}'

echo '{"singer_state": {"project_123456_issues": "2020-01-01"}}' > gitlab_state.json
meltano state set --force dev:tap-gitlab-to-target-jsonl --input-file gitlab_state.json

meltano state set --force dev:tap-gitlab-to-target-jsonl '{"invalid": "state"}'
# Error: Invalid state format: singer_state not found in top level of provided state.
# State must be valid JSON with a top-level 'singer_state' key.
# Use --no-validate to bypass this check.

meltano state set --force --no-validate dev:tap-gitlab-to-target-jsonl '{"custom": "format"}'
# WARNING: Skipping state validation. Invalid state may cause issues in future runs.
```

### `export`

Exports all state to stdout as JSON, suitable for backup/migration to another state backend. Output maps each state ID to its `completed`/`partial` state, preserving the internal split for lossless round-trips.

```bash
meltano state export > states.json
meltano --env-file src.env state export | meltano --env-file dst.env state import
```
```bash
meltano --env-file s3.env state export > states.json
meltano --env-file snowflake.env state import states.json

meltano state export > backup.json
```

### `import`

Imports state from a JSON file (or stdin), overwriting existing state for each state ID in the input. Expected format matches `meltano state export` output.

```bash
meltano state import <file>
meltano state export | meltano state import
```
`FILE` — path to a JSON file in `state export` format; omitted means read from stdin.
```bash
meltano state import backup.json
meltano --env-file s3.env state export | meltano --env-file snowflake.env state import
```

### Using `state` with Environments

Accepts `--environment`; `default_environment` is ignored.

---

## `test`

Runs tests for one or more plugins. A test is any command with a name starting with `test`.

```bash
meltano test --all                              # all tests, all plugins
meltano test <plugin1> <plugin2>                # all tests for selected plugins
meltano test --no-install <plugin1> <plugin2>   # prevent auto-install

meltano test <plugin>:<test-name>               # named test, single plugin
meltano test <plugin1>:<test-name1> <plugin2>:<test-name2>
```

### Using `test` with Environments

Accepts `--environment`; `default_environment` applies if not explicitly provided.

---

## `upgrade`

Upgrades Meltano and the project to the latest version. Without arguments:
- Upgrades the `meltano` package
- Updates files managed by file bundles
- Applies migrations to the system database

```bash
meltano upgrade
meltano upgrade --skip-package   # skip package upgrade

meltano upgrade package   # only Meltano package (can run outside project dir)
meltano upgrade files     # only file-bundle-managed files
meltano upgrade database  # only system database migrations
```

### Project directory requirements

`upgrade` and subcommands require running inside a project directory, except `meltano upgrade package`, which can run anywhere.

### Using `upgrade` with Environments

Does not run relative to an Environment. `--environment`/`default_environment` are ignored if set.

---

## `version`

Checks the installed Meltano version.

```bash
meltano --version
```
