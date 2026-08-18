# Migration Guides

Actionable migration steps and breaking changes for Meltano v2, v3, and v4, plus how to migrate an existing dbt project into a Meltano project. Organized by version — check the section relevant to your upgrade path.

## Migrating an Existing dbt Project into Meltano

Meltano uses suggested patterns for organizing your dbt project so it integrates well with core features like environments. You can organize your project however you choose, but this guide describes importing it to match the default transformer installation.

**Pre-requisite**: version-control your Meltano project first, so you can roll back if needed.

### Add dbt Transformer

Add your adapter-specific dbt variant (e.g. `dbt-postgres`), found on MeltanoHub:

```bash
meltano add dbt-<adapter_name>

# For example
meltano add dbt-postgres
```

Configure your transformer to include database names, connection credentials, etc. (see `transformation-and-orchestration.md`), or use `--interactive` to follow prompts:

```bash
meltano config set dbt-snowflake --interactive
```

Test your connection and credentials:

```bash
meltano invoke dbt-postgres debug
```

### Migrating dbt Code Into Meltano

The `initialize` command for a dbt transformer utility creates the expected scaffolding within `/transform`, including `dbt_project.yml` and `/profile/profiles.yml`. If you have an existing dbt project, skip `initialize` since you already have your own versions of these files — instead merge what you have with what Meltano provides and expects.

#### Meltano's Default Structure For dbt

Meltano expects dbt project files in these default directories (or you can update `dbt_project.yml` to follow your existing project's structure instead):

- `data` — seed files
- `models` — models
- `analysis` — analysis SQL that shouldn't be materialized
- `tests` — singular dbt tests
- `macros` — jinja macros
- `snapshots` — snapshot models

#### dbt Profiles

Meltano's default dbt project scaffolding comes with a `profiles.yml` configured to take advantage of the environments feature: you configure dbt using Meltano settings, and they're automatically passed to dbt based on the active Meltano environment. Meltano's dbt installation comes with pre-configured dbt targets mapped to the default environment names (dev, staging, prod), avoiding manual credential toggling and allowing sharing of settings/credentials across plugins.

#### Custom `dbt_project.yml` Configurations

If you had configurations in your `dbt_project.yml` (model materialization, target databases, schemas, etc.), copy them directly into your new Meltano `dbt_project.yml`. Meltano doesn't require this structure — any valid dbt project works — but this is the default recommended structure with base configurations for simple Meltano/dbt integration.

## Meltano 2.0 Migration Guide

Migrating existing "v1" projects to Meltano 2.0.

### Recommended

#### Migrate to an Adapter-Specific dbt Transformer

If you previously used the `dbt` or `dbt-<adapter>` Transformer, migrate to an adapter-specific utility plugin.

**Install dbt:**

```bash
# install adapter-specific dbt, e.g. for snowflake
meltano add dbt-snowflake
```

**Update your `dbt_project.yml`:**

Installing a new Transformer introduces two important files to `transform/`:

- A new `profiles.yml` at `transform/profiles/<adapter name>/profiles.yml`
- A new `dbt_project.yml` at `transform/dbt_project (<adapter name>).yml`

The new `profiles.yml` is only used by adapter-specific dbt executions (e.g. `dbt-snowflake`); your existing `profiles.yml` remains in use by your existing `dbt` Transformer plugin (via `elt` and `invoke`).

The new `dbt_project (<adapter name>).yml` will likely contain changes from your previous `dbt_project.yml`, especially if you haven't already upgraded to dbt v1.0. Consolidate both into a single `dbt_project.yml`. Since this file is used by both `dbt` and `dbt-<adapter>` Transformer plugins by default, ensure you're running an up-to-date `dbt` plugin if you intend to use both adapter-specific and legacy `dbt` installs together (not recommended).

Transform plugins continue to work as regular dbt packages, but adding new Transform plugins will currently re-add the legacy `dbt` Transformer plugin (tracked in meltano#3304). To avoid this, add Transforms as regular packages directly via dbt's package management.

**Remove the `dbt` Transformer plugin and associated files:**

```bash
# remove the transformer `dbt`
meltano remove transformer dbt

# remove the file bundle `dbt`
meltano remove files dbt
```

Removing a file bundle _does not_ remove any files from `transform/`. Manually remove `transform/profile/profiles.yml` to complete cleanup (adapter-specific installs come with their own `profiles.yml` in `transform/profiles/<adapter name>/profiles.yml`).

#### Migrate from orchestrators to utilities

If you've been using Meltano orchestrators to schedule ELT jobs, migrate to the new utilities: Airflow or Dagster (both on MeltanoHub).

### Removed

#### `model` and `dashboard` plugin types

These plugin types provided basic BI capabilities using Meltano UI. Removed in favor of existing/future 3rd party tools (e.g. Superset) for the same purpose.

#### `transform` support in `meltano elt`

Meltano 2.0 continues to support EL operations with `meltano elt`. For EL+T operations that also need to transform data, use `meltano run`.

#### `transform` support in Meltano schedules

Meltano 2.0 continues to support EL operations in schedules. For EL+T operations, use `meltano job add` to create a job definition, then specify the new job name in your schedule.

#### `env_aliases` in Plugin config

`env_aliases` is deprecated. It previously provided two functions:

1. Sourcing setting values from the terminal by a name other than the default environment variable (`<PLUGIN_NAME>_<SETTING_NAME>`).
2. Writing setting values into the plugin's runtime environment under a non-default environment variable name.

**For sourcing values**, use the default environment variables in most cases (found via `meltano config <plugin> list`). Where a non-default environment variable name must be used, reference it in `meltano.yml`:

```yaml
plugins:
  extractors:
    - name: tap-gitlab
      config:
        ultimate_license: $GITLAB_API_ULTIMATE_LICENSE
```

This takes the value from `GITLAB_API_ULTIMATE_LICENSE` and uses it to configure `tap-gitlab`'s `ultimate_license` setting.

**For writing values into the runtime environment** under a non-default name, use the `env:` key for setting definitions:

```yaml
plugins:
  extractors:
    - name: tap-gitlab
      settings:
        - name: ultimate_license
          env: GITLAB_API_ULTIMATE_LICENSE
```

This creates an environment variable `GITLAB_API_ULTIMATE_LICENSE` in the plugin's runtime environment with the configured value of `ultimate_license`.

**Updating your project**: Before v2.0, Meltano used `env_aliases` internally and in several common plugins. References to deprecated environment variables in your own project should be replaced with the corresponding default setting environment variable. Notable replacements include:

| Plugin | Deprecated | Replacement |
| --- | --- | --- |
| meltano | `MELTANO_LOG_LEVEL` | `MELTANO_CLI_LOG_LEVEL` |
| meltano | `MELTANO_LOG_CONFIG` | `MELTANO_CLI_LOG_CONFIG` |
| meltano | `MELTANO_API_HOSTNAME` | `MELTANO_UI_BIND_HOST` |
| meltano | `MELTANO_API_PORT` | `MELTANO_UI_BIND_PORT` |
| meltano | `MELTANO_READONLY` | `MELTANO_UI_READONLY` |
| meltano | `MELTANO_AUTHENTICATION` | `MELTANO_UI_AUTHENTICATION` |
| dbt-bigquery (meltano) | `DBT_PROFILES_DIR` | `DBT_BIGQUERY_PROFILES_DIR` |
| dbt-postgres (meltano) | `DBT_PROFILES_DIR` | `DBT_POSTGRES_PROFILES_DIR` |
| dbt-redshift (meltano) | `DBT_PROFILES_DIR` | `DBT_REDSHIFT_PROFILES_DIR` |
| dbt-snowflake (meltano) | `DBT_PROFILES_DIR` | `DBT_SNOWFLAKE_PROFILES_DIR` |
| tap-gitlab (meltano/meltanolabs) | `GITLAB_API_GROUPS` | `TAP_GITLAB_GROUPS` |
| tap-gitlab (meltano/meltanolabs) | `GITLAB_API_PROJECTS` | `TAP_GITLAB_PROJECTS` |
| tap-gitlab (meltano/meltanolabs) | `GITLAB_API_START_DATE` | `TAP_GITLAB_START_DATE` |
| tap-gitlab (meltano/meltanolabs) | `GITLAB_API_TOKEN` | `TAP_GITLAB_PRIVATE_TOKEN` |
| tap-gitlab (meltano/meltanolabs) | `GITLAB_API_ULTIMATE_LICENSE` | `TAP_GITLAB_ULTIMATE_LICENSE` |
| tap-google-analytics (meltano) | `GOOGLE_ANALYTICS_API_CLIENT_SECRETS` | `TAP_GOOGLE_ANALYTICS_KEY_FILE_LOCATION` |
| tap-google-analytics (meltano) | `GOOGLE_ANALYTICS_API_START_DATE` | `TAP_GOOGLE_ANALYTICS_START_DATE` |
| tap-google-analytics (meltano) | `GOOGLE_ANALYTICS_API_VIEW_ID` | `TAP_GOOGLE_ANALYTICS_VIEW_ID` |
| target-postgres (datamill-co) | `PG_ADDRESS` | `TARGET_POSTGRES_POSTGRES_HOST` |
| target-postgres (datamill-co) | `PG_DATABASE` | `TARGET_POSTGRES_POSTGRES_DATABASE` |
| target-postgres (meltano) | `PG_ADDRESS` | `TARGET_POSTGRES_HOST` |
| target-postgres (meltano) | `PG_DATABASE` | `TARGET_POSTGRES_DBNAME` |
| target-postgres (transferwise) | `PG_SCHEMA` | `TARGET_POSTGRES_DEFAULT_TARGET_SCHEMA` |
| target-snowflake (datamill-co) | `SF_ACCOUNT` | `TARGET_SNOWFLAKE_SNOWFLAKE_ACCOUNT` |
| target-snowflake (meltano) | `SF_ACCOUNT` | `TARGET_SNOWFLAKE_ACCOUNT` |
| target-snowflake (transferwise) | `SF_SCHEMA` | `TARGET_SNOWFLAKE_DEFAULT_TARGET_SCHEMA` |
| target-redshift (transferwise) | `TARGET_REDSHIFT_SCHEMA` | `TARGET_REDSHIFT_DEFAULT_TARGET_SCHEMA` |
| target-sqlite (meltano/meltanolabs) | `SQLITE_DATABASE` | `TARGET_SQLITE_DATABASE` |

> This is a representative subset of a much larger mapping table covering many plugins/variants (tap-adwords, tap-bigquery, tap-bing-ads, tap-csv, tap-pendo, tap-stripe, and more). If you rely on a specific deprecated variable not listed here, check `meltano config <plugin> list` for the current canonical name, or consult the full historical table in the Meltano docs source.

### CLI and API Changes

**Use `--state-id` instead of `--job_id`**: many references to "Job ID" were changed to the more accurate "State ID." Update any scripted/automated CLI workflows using `--job_id` to use `--state-id` instead.

**Schedule list format changes**: if you have custom orchestrator integrations based on `meltano schedule list`, note the output format of `meltano schedule list --format=json` changed with the addition of scheduled jobs support. It now includes a top-level `schedules` field with two nested array fields, `job` and `elt`:

```json
{
  "schedules": {
    "job": [
      {
        "name": "daily-doit",
        "interval": "@daily",
        "cron_interval": "0 0 * * *",
        "env": {},
        "job": {
          "name": "simple-demo",
          "tasks": [
            "tap-gitlab hide-gitlab-secrets target-jsonl",
            "tap-gitlab target-csv"
          ]
        }
      }
    ],
    "elt": [
      {legacy elt schedule entry remains unchanged}, ...
    ]
  }
}
```

## Meltano 3.0 Migration Guide

Migrating existing "v2" projects to Meltano 3.0.

### Changed

#### Using Postgres as a backend now requires installing Meltano with extra components

If already using Postgres (relying on `psycopg2`), install Meltano with the `psycopg2` extra:

```bash
pipx install "meltano[psycopg2]"
```

If setting a Postgres backend for the first time, use the `postgres` extra and the `postgresql+psycopg` URI scheme instead:

```bash
pipx install "meltano[postgres]"
meltano config meltano set database_uri postgresql+psycopg://<username>:<password>@<host>:<port>/<database>
```

#### Plugin lock files are now always required

Plugin lock files are now always required. Previously, Meltano fell back to retrieving the plugin definition from Meltano Hub if the lock file was missing — this caused issues when lock files weren't deployed to production and Meltano Hub was unavailable due to network restrictions.

**Migration steps:**

1. Enable the `ff.plugin_locks_required` feature flag:

   ```bash
   meltano config meltano set ff.plugin_locks_required true
   ```

2. Test your project still works as expected, e.g. by installing all plugins:

   ```bash
   meltano install
   ```

3. Generate all lock files for your project:

   ```bash
   meltano lock
   ```

4. (Optional) Remove the `ff.plugin_locks_required` feature flag after upgrading to v3, since it has no effect in v3.

> For custom plugins, you might need to add a `namespace` to the plugin definition.

### Removed

#### Target extra setting `target_schema`

In line with the deprecation of `meltano elt` in favor of `meltano el`, the `target_schema` extra setting of loaders has been removed. This should impact very few users, since `target_schema` was only used by the `dbt` transformer, deprecated in favor of adapter-specific dbt utilities.

**Migration steps**: in the `dbt` transformer plugin configuration, set `source_schema` to the appropriate environment variable for your target (e.g. `$MELTANO_LOAD__DEFAULT_TARGET_SCHEMA` for Postgres).

#### The Meltano UI

Before v3.0.0, Meltano included a web UI (`meltano ui`). Deprecated in v2.12.0, removed in v3.0.0. Everything previously possible through the UI is possible via the CLI, or by directly editing `meltano.yml`.

## Meltano 4.0 Migration Guide

Breaking changes and migration steps for Meltano 4.0.0.

### Breaking Changes

#### Python 3.9 support dropped

Meltano 4.0 requires Python 3.10 or later. If still on Python 3.9, upgrade to 3.10, 3.11, 3.12, 3.13, or 3.14 before upgrading Meltano.

#### Docker image changes

The `psycopg2` extra has been removed from Meltano's Docker images to reduce image size. If you need PostgreSQL support in Docker, install it explicitly:

```dockerfile
FROM meltano/meltano:latest
RUN uv pip install psycopg2-binary
```

Alternatively, use the `postgres` extra and the `postgresql+psycopg` URI scheme with psycopg3.

### Removed Deprecated Features

#### Deprecated CLI flags and arguments

Removed:

- `meltano lock --all` flag (use `meltano lock` without flags — it locks all plugins by default)
- `meltano install - <plugin_name>` syntax (use `meltano install <plugin_name>`)
- Plugin type positional argument in various commands (use `--plugin-type` option instead)

Update your scripts and workflows to use the new syntax before upgrading.

#### Console output changes

The default console logger now displays fewer keys to reduce visual clutter. If you rely on specific keys being displayed, customize the output format using custom logging configuration (see `deployment-and-operations.md`).

#### Config command argument order

The order of positional arguments for `meltano config` subcommands changed. The plugin name now comes before the setting name:

```bash
# Old
meltano config set <setting> <plugin_name> <value>

# New
meltano config set <plugin_name> <setting> <value>
```

This makes the command more intuitive and consistent with other Meltano commands.

#### Plugin logger naming

Plugin subprocess loggers have been renamed from `meltano.runner.<plugin_name>` to `meltano.plugins.<stream>.<type>.<name>`, where `<stream>` is either `stdout` or `stderr` — separating standard output and error streams into distinct loggers.

Update custom logging configurations that filter on logger names:

```yaml
# Old
loggers:
  meltano.runner.tap-github:
    level: INFO

# New
loggers:
  meltano.plugins.stdout.extractor.tap-github:
    level: INFO
```

#### Schedule `start_date` removed

The `start_date` attribute has been removed from schedule definitions in `meltano.yml`. This attribute was unused by Meltano and should be removed from your schedule configurations.

### Platform-dependent log location

Meltano now stores logs in a platform-appropriate location following OS conventions:

- **macOS**: `~/Library/Logs/Meltano`
- **Linux**: `~/.local/state/meltano/logs`

Use the `meltano logs` command to view job logs easily.

### Auto-lock plugin definitions

Plugin definitions are now automatically locked when you add or update plugins, ensuring reproducible deployments without manual `meltano lock` invocations.

### Migration Checklist

1. Verify you're running Python 3.10 or later
2. Update any custom logging configurations to use new logger names
3. Remove `start_date` from schedule definitions in `meltano.yml`
4. Update scripts using deprecated CLI syntax:
   - Replace `meltano lock --all` with `meltano lock`
   - Replace `meltano install - <plugin>` with `meltano install <plugin>`
   - Replace positional plugin type arguments with `--plugin-type`
5. Update `meltano config` commands to use new argument order
6. If using Docker with PostgreSQL, add explicit `psycopg2-binary` installation
7. Test your pipelines in a development environment before upgrading production

For a complete list of changes, see the v4.0.0 changelog on GitHub.
