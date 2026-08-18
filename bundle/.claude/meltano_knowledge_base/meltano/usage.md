# Usage: Plugin Management and Configuration

Core day-to-day Meltano workflows: adding/installing/managing plugins in a project, and how plugin and Meltano configuration is layered, sourced, and overridden.

## Plugin Management

Meltano takes a modular approach to data engineering, where your project and pipelines are composed of plugins of different types — most notably **extractors** (Singer taps), **loaders** (Singer targets), and **utilities** (like dbt for transformations, Airflow/Dagster/etc. for orchestration, and much more on MeltanoHub).

Your project's plugins are defined in your `meltano.yml` project file, and are installed inside the `.meltano` directory. They can be managed using various CLI commands.

### Adding a plugin to your project

You can add a new plugin to your project using `meltano add`, or by directly modifying your `meltano.yml` project file and installing the new plugin using `meltano install`.

- If you'd like to add a **discoverable plugin** supported by Meltano out of the box (see the Extractors and Loaders pages on MeltanoHub), see "Discoverable plugins" below.
- If you'd like to add a **custom plugin** that Meltano isn't familiar with yet, like an arbitrary Singer tap or target, see "Custom plugins" below.
- If you'd like your new plugin to **inherit from an existing plugin** in your project, so it can reuse the same package but override (parts of) its configuration, see "Plugin inheritance" below.

#### Discoverable plugins

Discoverable plugins can be added to your project by simply providing `meltano add` with their name. Meltano will automatically detect the plugin type:

```bash
# Simplified syntax (Meltano 3.8+) - plugin type is automatically detected
meltano add <name>

# For example:
meltano add tap-gitlab        # Automatically detected as extractor
meltano add target-postgres   # Automatically detected as loader
meltano add dbt-snowflake     # Automatically detected as utility
meltano add airflow           # Automatically detected as utility

# Explicit plugin type specification for disambiguation when needed
meltano add --plugin-type <type> <name>

# For example:
meltano add --plugin-type extractor tap-gitlab
meltano add --plugin-type loader target-postgres
meltano add --plugin-type utility dbt-snowflake
meltano add --plugin-type utility airflow
```

For Meltano 3.7 and earlier, the plugin type was specified positionally:

```bash
meltano add <name>

# For example:
meltano add tap-gitlab
meltano add target-postgres
meltano add dbt-snowflake
meltano add airflow
```

This adds a shadowing plugin definition to your `meltano.yml` project file under the `plugins` property, inside an array named after the plugin type:

```yaml title="meltano.yml"
plugins:
  extractors:
  - name: tap-gitlab
    variant: meltano
    pip_url: git+https://gitlab.com/meltano/tap-gitlab.git
  loaders:
  - name: target-postgres
    variant: datamill-co
    pip_url: singer-target-postgres
  utilities:
  - name: dbt-snowflake
    variant: dbt-labs
  - name: airflow
    variant: apache
```

If multiple variants of the discoverable plugin are available, the `variant` property is automatically set to the name of the default variant (known to work well and recommended for new users), so your project is pinned to a specific package and its base plugin description. If `variant` were omitted, Meltano falls back on the _original_ supported variant instead, which does not necessarily match the default.

The package's `pip_url` (its `pip install` argument) is repeated here for convenience, since you may want to update it to point at a custom fork or pin the package to a specific version. If this property is omitted, it's inherited from the discoverable base plugin description identified by the `name` (and `variant`).

Directly adding a plugin to `meltano.yml` and installing it using `meltano install [<type>|-] <name>` has the same effect as adding it using `meltano add`.

##### Variants

If multiple variants of a discoverable plugin are available, choose a specific (non-default) variant using `--variant` on `meltano add`:

```bash
# With automatic type detection (3.8+)
meltano add <name> --variant <variant>

# For example:
meltano add target-postgres --variant=transferwise  # Type automatically detected as loader

# With explicit type specification for disambiguation
meltano add --plugin-type loader target-postgres --variant=transferwise
```

For 3.7 and earlier:

```bash
meltano add loader <name> --variant <variant>

# For example:
meltano add loader target-postgres --variant=transferwise
```

This is reflected in the `variant` and `pip_url` properties in `meltano.yml`:

```yaml title="meltano.yml"
plugins:
  loaders:
  - name: target-postgres
    variant: transferwise
    pip_url: pipelinewise-target-postgres
```

##### Explicit inheritance

By default, plugins in your project implicitly inherit their base plugin descriptions from discoverable plugins by reusing their names (known as shadowing).

Alternatively, if you'd like to give the plugin a more descriptive name in your project, use `--inherit-from` (or `--as`) on `meltano add` to explicitly inherit from the discoverable plugin instead:

```bash
# With automatic type detection (3.8+)
meltano add <name> --inherit-from <discoverable-name>
# Or equivalently:
meltano add <discoverable-name> --as <name>

# With explicit type specification for disambiguation
meltano add --plugin-type <type> <name> --inherit-from <discoverable-name>
# Or equivalently:
meltano add --plugin-type <type> <discoverable-name> --as <name>

# For example:
meltano add tap-postgres--billing --inherit-from tap-postgres
meltano add tap-postgres --as tap-postgres--billing
```

For 3.7 and earlier:

```bash
meltano add <type> <name> --inherit-from <discoverable-name>
# Or equivalently:
meltano add <type> <discoverable-name> --as <name>

# For example:
meltano add extractor tap-postgres--billing --inherit-from tap-postgres
meltano add extractor tap-postgres --as tap-postgres--billing
```

The corresponding inheriting plugin definition in `meltano.yml` uses `inherit_from`:

```yaml title="meltano.yml"
plugins:
  extractors:
  - name: tap-postgres--billing
    inherit_from: tap-postgres
    variant: transferwise
    pip_url: pipelinewise-tap-postgres
```

Note that the `variant` and `pip_url` properties were populated automatically by `meltano add` as described above.

###### Multiple variants

If you'd like to use multiple variants of the same discoverable plugin in your project at the same time: since plugins in your project need unique names, a discoverable plugin can only be shadowed once, but it can be inherited from multiple times, with each plugin free to choose its own variant:

```bash
meltano add target-snowflake --variant=transferwise --as target-snowflake--transferwise
meltano add target-snowflake --variant=meltanolabs --as target-snowflake--meltanolabs
```

For 3.7 and earlier:

```bash
meltano add loader target-snowflake --variant=transferwise --as target-snowflake--transferwise
meltano add loader target-snowflake --variant=meltanolabs --as target-snowflake--meltanolabs
```

Assuming a regular (shadowing) `target-snowflake` was added before, the resulting inheriting plugin definitions in `meltano.yml` look like:

```yaml title="meltano.yml"
plugins:
  loaders:
  - name: target-snowflake
    variant: datamill-co
    pip_url: target-snowflake
  - name: target-snowflake--transferwise
    inherit_from: target-snowflake
    variant: transferwise
    pip_url: pipelinewise-target-snowflake
  - name: target-snowflake--meltano
    inherit_from: target-snowflake
    variant: meltano
    pip_url: git+https://gitlab.com/meltano/target-snowflake.git
```

The `--variant` option and `variant` property are crucial here: since `inherit_from` can also be used to inherit from another plugin in the project, `inherit_from: target-snowflake` by itself would result in the new plugin inheriting from the existing `target-snowflake` plugin (using the `datamill-co` variant) instead of the discoverable plugin. Had there been no `target-snowflake` plugin in the project yet, `inherit_from: target-snowflake` would necessarily refer to the discoverable plugin, but without a `variant` the _original_ variant would be used rather than the default or a specific chosen one — just like when shadowing with a `name` but no `variant`.

#### Custom plugins

Custom plugins for packages that aren't discoverable yet, like arbitrary Singer taps and targets, can be added using the `--custom` option on `meltano add`:

```bash
meltano add --custom <name>

# For example:
meltano add --custom tap-covid-19
meltano add --custom target-bigquery--custom

# If you're using Docker, don't forget to mount the project directory,
# and ensure that interactive mode is enabled so that Meltano can ask you
# additional questions about the plugin and get your answers over STDIN:
docker run --interactive -v $(pwd):/project -w /project meltano/meltano add --custom tap-covid-19
```

For 3.7 and earlier:

```bash
meltano add --custom <type> <name>

# For example:
meltano add --custom extractor tap-covid-19
meltano add --custom loader target-bigquery--custom
```

Since Meltano doesn't have the base plugin description for the package yet, `meltano add --custom` will ask you to find and provide this metadata yourself:

```console
$ meltano add --custom extractor tap-covid-19
Adding new custom extractor with name 'tap-covid-19'...

Specify the plugin's namespace, which will serve as the:
- identifier to find related/compatible plugins
- default database schema (`load_schema` extra),
  for use by loaders that support a target schema

Hit Return to accept the default: plugin name with underscores instead of dashes

(namespace) [tap_covid_19]: tap_covid_19

Specify the plugin's `pip install` argument, for example:
- PyPI package name:
  tap-covid-19
- Git repository URL:
  git+https://gitlab.com/meltano/tap-covid-19.git
- local directory, in editable/development mode:
  -e extract/tap-covid-19
- 'n' if using a local executable (nothing to install)

Default: plugin name as PyPI package name

(pip_url) [tap-covid-19]: -e extract/tap-covid-19

Specify the plugin's executable name

Default: name derived from `pip_url`

(executable) [tap-covid-19]: tap-covid-19

Specify the tap's supported Singer features (executable flags), for example:
  `catalog`: supports the `--catalog` flag
  `discover`: supports the `--discover` flag
  `properties`: supports the `--properties` flag
  `state`: supports the `--state` flag

To find out what features a tap supports, reference its documentation or try one
of the tricks under "how to test a tap".

Multiple capabilities can be separated using commas.

Default: no capabilities

(capabilities) [[]]: catalog,discover,state

Specify the tap's supported settings (`config.json` keys)

Multiple setting names (keys) can be separated using commas.

A setting kind can be specified alongside the name (key) by using the `:` delimiter,
e.g. `port:integer` to set the kind `integer` for the name `port`

Supported setting kinds:
string | integer | boolean | decimal | date_iso8601 | email | password | oauth | options | file | array | object | hidden

- Credentials and other sensitive setting types should use the password kind.
- If not specified, setting kind defaults to string.
- Nested properties can be represented using the `.` separator, e.g. `auth.username` for `{ "auth": { "username": value } }`.
- To find out what settings a tap supports, reference its documentation.

Default: no settings

(settings) [[]]: api_token:password,user_agent:string,start_date:date_iso8601
Added extractor 'tap-covid-19' to your Meltano project

Installing extractor 'tap-covid-19'...
Installed extractor 'tap-covid-19'
```

If you're adding a Singer tap or target listed on Singer's index of taps or targets, simply providing the package name as `pip_url` and `executable` usually suffices. The plugin's `name` also typically matches the package name, but you can change it to be more descriptive.

If it's a tap or target you've developed yourself, set `pip_url` to either a Git repository URL or local directory path. Adding the `-e` flag ahead of the local path installs the package in editable mode.

This adds a custom plugin definition to `meltano.yml`:

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

The `pip_url`, `executable`, `capabilities`, and `settings` properties constitute the plugin's base plugin description: everything Meltano needs to know to use the package as a plugin.

> Once you've got the plugin working in your project, consider adding it to Meltano Hub to make it discoverable and supported out of the box for new users.

#### Plugin inheritance

To add a new plugin that inherits from an existing plugin (so it can reuse the same package but override parts of its configuration), use `--inherit-from` on `meltano add`:

```bash
meltano add <name> --inherit-from <existing-name>

# For example:
meltano add tap-ga--client-foo --inherit-from tap-google-analytics
meltano add tap-ga--client-bar --inherit-from tap-google-analytics
meltano add tap-ga--client-foo--project-baz --inherit-from tap-ga--client-foo
```

For 3.7 and earlier:

```bash
meltano add <type> <name> --inherit-from <existing-name>

# For example:
meltano add extractor tap-ga--client-foo --inherit-from tap-google-analytics
```

The corresponding inheriting plugin definitions in `meltano.yml`:

```yaml title="meltano.yml"
plugins:
  extractors:
  - name: tap-google-analytics
    variant: meltano
    pip_url: git+https://gitlab.com/meltano/tap-google-analytics.git
  - name: tap-ga--client-foo
    inherit_from: tap-google-analytics
  - name: tap-ga--client-bar
    inherit_from: tap-google-analytics
  - name: tap-ga--client-foo--project-baz
    inherit_from: tap-ga--client-foo
```

The `--inherit-from` option and `inherit_from` property can also be used to explicitly inherit from a discoverable plugin (see "Explicit inheritance" above).

#### Updating plugins

You can update a plugin in your project using the `--update` option. Updating a plugin re-adds it to your project — that is:

- Updates the plugin lock file (same as `meltano lock --update`)
- Updates the plugin entry in `meltano.yml`, without overwriting any user-defined config or extras

> Plugin lock files may include a `requires_meltano` field specifying the minimum Meltano version required by that plugin. If your current Meltano version doesn't meet the plugin's requirements, Meltano will exit with an error when trying to invoke the plugin.

```bash
meltano add --update <type> <name>

# For example:
meltano add --update extractor tap-gitlab
```

### Installing your project's plugins

Whenever you add a new plugin using `meltano add`, it's installed into your project's `.meltano` directory automatically.

However, since this directory is included in your project's `.gitignore` file by default, you'll need to explicitly run `meltano install` before any other `meltano` commands whenever you clone or pull an existing Meltano project from version control, to install (or update) all plugins specified in `meltano.yml`.

To install a specific plugin, use `meltano install <name>`, e.g. `meltano install tap-gitlab target-postgres`. Meltano automatically detects the plugin type. Subsequent calls to `meltano install` will upgrade a plugin to its latest version, if any. To completely uninstall and reinstall a plugin, use `--clean`.

> **Deprecated syntax** (removed in Meltano v4):
>
> | Deprecated Syntax | Use Instead |
> | --- | --- |
> | `meltano install <plugin_type> <plugin_name>` | `meltano install --plugin-type <plugin_type> <plugin_name>` |
> | `meltano install - <plugin_name>` | `meltano install <plugin_name>` |

### Pinning a plugin to a specific version

When you add a plugin, the plugin definition's `pip_url` property in `meltano.yml` typically points at a PyPI package or Git repository without specifying a version, to ensure you always get the latest. This makes sense initially, but can lead to unwelcome surprises as your pipeline may break when a new package version introduces a bug or backward-incompatible behavior.

To ensure `meltano install` always installs the same version originally used, modify the plugin definition's `pip_url` to include a version identifier.

#### PyPI package

If `pip_url` is a package name, e.g. `tap-shopify`, add an `==<version>` or `~=<version>` version specifier:

```yaml
# Before:
pip_url: tap-shopify

# After:
pip_url: tap-shopify==1.2.6 # Always install version 1.2.6

# Alternatively:
pip_url: tap-shopify~=1.2.6 # Install 1.2.6 or a newer version in the 1.2.x range
```

#### Git repository

If `pip_url` is a `git+http(s)` URL, add an `@<tag>` or `@<sha>` Git ref specifier:

```yaml
# Before:
pip_url: git+https://gitlab.com/meltano/tap-gitlab.git
pip_url: git+https://github.com/adswerve/target-bigquery.git

# After:
pip_url: git+https://gitlab.com/meltano/tap-gitlab.git@v0.9.11
pip_url: git+https://github.com/adswerve/target-bigquery.git@v0.10.2

# Alternatively, using a commit SHA:
pip_url: git+https://gitlab.com/meltano/tap-gitlab.git@2657b89e8896face4ce320a03b8413bbc196cec9
pip_url: git+https://github.com/adswerve/target-bigquery.git@3df97b951b7eebdfa331a1ff570f1fe3487d632f
```

### Installing plugins from a custom Python Package Index (PyPI)

To fetch packages from a custom PyPI, set the `PIP_INDEX_URL` environment variable to your custom URL before running `meltano install`.

> Starting with Meltano 3.4.0, `PIP_*` environment variables can also be set in your project's `.env` file.

In a `Dockerfile`:

```dockerfile
ARG PIP_INDEX_URL=<your_custom_pypi_url>
RUN meltano install
```

### Configuring _uv_ virtual environment options

Starting with Meltano 3.8, the default virtual environment backend is `uv`, which creates virtual environments significantly faster than the traditional `virtualenv` backend.

By default, `uv` creates lightweight virtual environments without bundling `pip`, `setuptools`, or `wheel` to optimize installation speed. Some plugins or workflows may require these tools to be available (e.g., notebooks that run `pip install` commands).

You can configure `uv`'s virtual environment behavior using environment variables, set in your project's `.env` file, your shell environment, or the top-level `env` key in `meltano.yml`:

```yaml
# meltano.yml
version: 1
env:
  UV_VENV_SEED: "1"
  UV_EXCLUDE_NEWER: "2025-01-01T00:00:00Z"

plugins:
  extractors:
    - name: tap-gitlab
      # ...
```

```bash
# .env
UV_VENV_SEED=1
UV_EXCLUDE_NEWER=2025-01-01T00:00:00Z
```

```bash
# Shell
export UV_VENV_SEED=1
export UV_EXCLUDE_NEWER=2025-01-01T00:00:00Z
```

#### `UV_VENV_SEED`

Controls whether seed packages (`pip`, `setuptools`, and `wheel`) are installed into virtual environments created by `uv venv`.

**When to use it:**
- Your plugin or utility needs to run `pip install` commands within its virtual environment
- You're using Jupyter notebooks that install dependencies dynamically
- You need backwards compatibility with workflows that assume `pip` is available

Note that `setuptools` and `wheel` are excluded from Python 3.12+ environments by default, even when seeding is enabled.

#### `UV_EXCLUDE_NEWER`

Limits package resolution to versions published before a specific date, ensuring reproducible builds by preventing newer package versions from being considered during installation.

**When to use it:**
- You want consistent builds across different environments
- You need to avoid issues caused by recently published package versions
- You're troubleshooting dependency resolution problems

The date should be ISO 8601 format (e.g., `2025-01-01T00:00:00Z`).

**Alternative approach:** If you only need `pip` available and don't want to enable full seeding, add `pip` to your plugin's `pip_url` configuration:

```yaml
plugins:
  utilities:
  - name: notebook
    pip_url: jupyter pip
```

This installs `pip` as a dependency of the plugin without requiring `UV_VENV_SEED`.

### Removing a plugin from your project

Remove a plugin using `meltano remove`. The plugin type is automatically inferred from the plugin name.

```bash
# Plugin type is automatically inferred (3.8+)
meltano remove <name>
meltano remove <name> <name_two>

# For example:
meltano remove tap-gitlab
meltano remove target-postgres target-csv
```

For 3.7 and earlier:

```bash
meltano remove <type> <name>
meltano remove <type> <name> <name_two>

# For example:
meltano remove extractor tap-gitlab
meltano remove loader target-postgres target-csv
```

Since the `plugins` section of `meltano.yml` determines the plugins that make up your project, you can still manually remove a plugin by deleting its entry from this file. Traces of the plugin may remain in the other locations mentioned above.

### Using a custom fork of a plugin

If you've forked a plugin's repository and made changes, update your project to use your fork instead of the canonical source:

1. Modify the plugin definition's `pip_url` in `meltano.yml` to point at your fork using a `git+http(s)` URL, with an optional branch or tag name:

   ```yaml title="meltano.yml"
   plugins:
     extractors:
     - name: tap-gitlab
       variant: meltano
       pip_url: git+https://gitlab.com/meltano/tap-gitlab.git
       # pip_url: git+https://gitlab.com/meltano/tap-gitlab.git@ref-name
   ```

   If your plugin source is in a private repository, you have two options:

   - Continue to authenticate over HTTP(S), storing your credentials in a `.netrc` file in your home directory:

     ```bash
     machine <hostname> # e.g. gitlab.com or github.com
     login <username>
     password <personal-access-token-or-password>
     ```

   - Authenticate using SSH instead, specifying a `git+ssh` URL:

     ```yaml
     pip_url: git+ssh://git@gitlab.com/meltano/tap-gitlab.git
     ```

     Depending on your git provider (such as Azure Repos), some `git+ssh` URLs may contain a colon, which can cause errors with `pip`. Fix by replacing the colon with a forward slash:

     ```
     # Instead of:
     git+ssh://git@ssh.dev.azure.com:v3/my_org/

     # Use:
     git+ssh://git@ssh.dev.azure.com/v3/my_org/
     ```

2. Reinstall the plugin from the new `pip_url`:

   ```bash
   meltano install [--plugin-type=<type>] <name>

   # For example:
   meltano install tap-gitlab
   ```

If your fork supports additional settings, set them as custom settings (see "Custom settings" below).

### Switching from one variant to another

The default variant of a discoverable plugin is recommended for new users but may not always be a perfect fit.

If you've already added one variant and want to use another, add the new variant as a separate plugin, or switch your existing plugin over:

1. Modify the plugin definition's `variant` and `pip_url` properties in `meltano.yml`:

   ```yaml title="meltano.yml"
   # Before:
   plugins:
     loaders:
     - name: target-postgres
       variant: datamill-co
       pip_url: singer-target-postgres

   # After:
   plugins:
     loaders:
     - name: target-postgres
       variant: meltano
       pip_url: git+https://github.com/meltano/target-postgres.git # Optional
   ```

   If you don't know the new variant's `pip_url`, remove this property entirely so Meltano falls back on the default.

2. Reinstall the plugin from the new `pip_url`:

   ```bash
   meltano install [--plugin-type=<type>] <name>

   # For example:
   meltano install target-postgres
   ```

3. View the current configuration using `meltano config list <name>` to see if it's still valid:

   ```bash
   meltano config list <name>

   # For example:
   meltano config list target-postgres
   ```

   Because different variants often use different setting names, you'll likely see some settings used by the old variant show up as custom settings (indicating they're not supported by the new variant), while settings the new variant expects show up with a `None` or default value.

4. Modify the plugin's configuration in `meltano.yml` to use the new setting names:

   ```yaml
   # Before:
   config:
     postgres_host: postgres.example.com
     postgres_port: 5432
     postgres_username: my_user
     postgres_database: my_database

   # After:
   config:
     host: postgres.example.com
     port: 5432
     user: my_user
     dbname: my_database
   ```

   If any old settings are stored elsewhere (like a sensitive setting in `.env`), unset the old setting and set the new one:

   ```bash
   meltano config unset <name> <old_setting>
   meltano config set <name> <setting> <value>

   # For example:
   meltano config unset target-postgres postgres_password
   meltano config set target-postgres password my_password
   ```

   Keep doing this until `meltano config list <name>` shows a valid configuration for the new variant, without any of the old variant's settings remaining as custom settings.

## Configuration

Meltano is responsible for managing the configuration of all of a project's plugins. It knows what settings are supported by each plugin, and how and when different types of plugins expect to be fed that configuration.

Since this also goes for extractors and loaders, you do not need to manually craft the `config.json` files expected by Singer taps and targets — Meltano generates them on the fly whenever an extractor or loader is used through `meltano run` or `meltano invoke`.

If the plugin is discoverable, Meltano already knows what settings it supports. If it's a custom plugin, you provide the names of the supported configuration options yourself.

Use `meltano config list <plugin>` to list all available settings with their names, environment variables, and current values. `meltano config print <plugin>` prints the current configuration in JSON format. If supported by the plugin type, configuration can be tested using `meltano config test <plugin>`.

Meltano itself can be configured as well — see the Settings Reference for details.

### Configuration layers

To determine the values of settings, Meltano looks in 4 main places (and one optional one), each taking precedence over the next:

1. **Environment variables**, set through your shell at `meltano run` runtime, your project's `.env` file, a scheduled pipeline's `env` dictionary, or any other method.
   - Use `meltano config list <plugin>` to list the available variable names, typically of the format `<PLUGIN_NAME>_<SETTING_NAME>`.
2. **Your `meltano.yml` project file**, under the plugin's `config` key.
   - Inside values, environment variables can be referenced as `$VAR` (as a single word) or `${VAR}` (inside a word).
   - Configuration for Meltano itself is stored at the root level of `meltano.yml`.
   - You can use Meltano Environments to manage different configurations depending on testing/deployment strategy. If values are provided in both the top-level plugin configuration _and_ the environment-level plugin configuration, the environment-level value takes precedence.
3. **Your project's system database**, which (among other things) stores configuration set using `meltano config set <plugin>` when the project is deployed as read-only.
   - Configuration for Meltano itself cannot be stored in the system database.
4. _If the plugin inherits from another plugin in your project_: **The parent plugin's own configuration**
5. **The default `value`s** set in the plugin's `settings` metadata.
   - Definitions of discoverable plugins can be found on Meltano Hub.
   - Custom plugin definitions can be found in your `meltano.yml` project file.
   - `meltano config list <plugin>` lists the default values.

Configuration that is _not_ environment-specific or sensitive should be stored in `meltano.yml` and checked into version control. Sensitive values like passwords and tokens are most appropriately stored in the environment, `.env`, or the system database.

`meltano config set <plugin>` will automatically store configuration in `meltano.yml` or `.env` as appropriate.

You can customize how `meltano.yml` is formatted (indentation, spacing, etc.) using Meltano's user YAML configuration (see below).

### Overriding discoverable plugin properties

Starting with Meltano `2.0`, you can override the properties of discoverable plugins, such as their `capabilities` and `settings_group_validation`, and extend their default `settings`:

```yaml
plugins:
  extractors:
  - name: tap-example
    variant: meltanolabs
    capabilities:  # This will override the capabilities declared in the lockfile
    - state
    - discover
    - catalog
    settings:  # These will be appended to the settings declared in the lockfile
    - name: my-new-setting
      kind: object
      value:
        key: value
```

All overrides replace the values stored in the lockfile, except for `settings`, which extend the base definitions. If there's a collision on name, the setting is taken from the override definition in `meltano.yml` and used at runtime, while the lockfile setting definition is discarded.

### Environment variables

When you run an executable on your system, environment variables can be used to pass along arbitrary key-value data to the new process.

Meltano reads settings from environment variables when you run the `meltano` command, and populates them when it evaluates plugin configuration and invokes plugin executables. Meltano also supports specifying environment variables under the `env:` keys of `meltano.yml`, a Meltano Environment, or on the Plugin.

#### Specifying environment variables

In addition to the terminal environment and the `.env` file, Meltano supports specifying environment variables at these configuration levels:

```yaml
env:
  # root level env
  MY_ENV_VAR: top_level_env_var
plugins:
  extractors:
  - name: tap-google-analytics
    variant: meltano
    env:
      # root level plugin env
      MY_ENV_VAR: plugin_level_env_var
  loaders:
  - name: target-postgres
    variant: transferwise
    pip_url: pipelinewise-target-postgres
environments:
- name: dev
  env:
    # environment level env
    MY_ENV_VAR: environment_level_env_var
  config:
    plugins:
      extractors:
        - name: tap-google-analytics
          variant: meltano
          env:
            # environment level plugin env
            MY_ENV_VAR: environment_level_plugin_env_var
schedules:
- name: daily-google-analytics-load
  interval: '@daily'
  extractor: tap-google-analytics
  loader: target-postgres
  transform: skip
  start_date: 2024-08-24 00:00:00
  env:
    SCHEDULE_SPECIFIC_ENV_VAR: schedule_specific_value
```

Environment levels within `meltano.yml` resolve in order of precedence (within a plugins context):

```
- environment level plugin env # highest
- environment level env
- root level plugin env
- root level env
- schedule level env
- .env file
- terminal env # lowest
```

This allows you to override environment variables per plugin and per environment, as needed for your use case.

##### Environment variable expansion

Environment variable values within a given layer of `meltano.yml` can inherit values from other layers. For example, if your terminal environment has `TERMINAL_ENVIRONMENT_VARIABLE` set to `1` and you add:

```yaml
environments:
  - name: dev
    env:
      INHERITED: ${TERMINAL_ENVIRONMENT_VARIABLE}2
```

then `INHERITED` expands to `12` in the `dev` environment.

Environment variables are inherited across layers in this order, where each level's values are expanded using values from the layers above it:

```
- terminal env and .env
- root-level env in meltano.yml
- active environment env
- root-level plugin-level env
- active environment-level plugin-level env
```

Example illustrating value expansion:

```yaml
env:
  # Level 2: top-level `env:`
  # Inherits from terminal context
  LEVEL_NUM: "2"                  #  '2'
  STACKED: "${STACKED}2"          # '12'
plugins:
  extractors:
    - name: tap-foobar
      env:
        # Level 4: plugin-level `env:`
        # Inherits from an environment-level `env:` if an environment is active
        # Inherits directly from top-level `env:` if no environment is active
        LEVEL_NUM: "4"            #    '4'
        STACKED: "${STACKED}4"    # '1234'
environments:
  - name: prod
    env:
      # Level 3: environment-level `env:`
      # Inherits from top-level `env:`
      LEVEL_NUM: "3"              #   '3'
      STACKED: "${STACKED}3"      # '123'
    config:
      plugins:
        extractors:
          - name: tap-foobar
            env:
              # Level 5: environment-level plugin `env:`
              # Inherits from (global) plugin-level `env:`
              LEVEL_NUM: "5"          #     '5'
              STACKED: "${STACKED}5"  # '12345'
```

Note that the resolution and inheritance behavior of environment variables set via `env` keys in `meltano.yml` differ from the resolution and inheritance behavior of `config` or `settings` keys (see "Configuration layers" above).

Because settings and environment variable behavior can become complex when set in multiple places, `meltano invoke` provides a `--print-var` option to easily inspect what value is being supplied for a given environment variable within your plugin's invocation environment at runtime.

###### Environment variable expansion within `pip_url`

In addition to affecting environment variables at runtime and `config`/`settings` values, environment variables can be expanded within the value of a plugin's `pip_url`. The same inheritance order applies.

This is useful for using a different `pip_url` per environment (e.g. to change which git branch of a plugin repository is used):

```yaml
pip_url: "git+https://github.com/MeltanoLabs/tap-github.git@${TAP_GITHUB_GIT_REV}"
```

Another use is supplying credentials for a private Python package index:

```yaml
pip_url: "https://${NEXUS_USERNAME}:${NEXUS_PASSWORD}@nexus.example.com/simple"
```

#### Configuring settings

Meltano looks at the environment variables it was executed with, and those specified in `.env`, to determine the values of its own settings and those of its plugins.

Any setting can be configured by specifying an environment variable named `<PLUGIN_NAME>_<SETTING_NAME>`, with characters other than alphanumeric and underscores replaced with underscores, e.g. `TAP_GITLAB_API_URL` for extractor `tap-gitlab`'s `api_url` setting:

```bash
export <PLUGIN_NAME>_<SETTING_NAME>=<value>

# For example:
export TAP_GITLAB_API_URL=https://gitlab.example.com
```

Plugins can also specify alternative variables (aliases) for their settings, to match existing usage or variables expected by plugin executables. Use `meltano config list <plugin>` to list all available settings for a plugin along with their variables, in order of precedence.

Since environment variable values are always strings, Meltano casts values to the appropriate type before passing them on to the plugin.

To verify that environment variables will be picked up as intended, test them with `meltano config print <plugin>` before running `meltano run` or `meltano invoke`.

##### Settings Aliases

Aliases allow configuration values to be set via one of multiple keys. Environment variable aliases are listed next to the canonical names in the output of `meltano config list <plugin>`. They can be defined via the `aliases` key in a custom plugin's `settings` configuration:

```yaml
# meltano.yml
---
plugins:
  extractors:
  - name: my-custom-tap
    namespace: my_custom_tap
    pip_url: git+https://github.com/my-organization/my-custom-tap.git
    executable: my-custom-tap
    capabilities:
    - discover
    - catalog
    settings:
    - name: password
      kind: string
      sensitive: true
    - name: my_custom_tap_username
      aliases: [custom_tap_username, username]
```

Within a given configuration layer, a setting can be set via only a single name, whether canonical or an alias. Given the custom extractor above, `my_custom_tap_username` could be set via `MY_CUSTOM_TAP_MY_CUSTOM_TAP_USERNAME`, `MY_CUSTOM_TAP_CUSTOM_TAP_USERNAME`, or `MY_CUSTOM_TAP_USERNAME`.

If more than one of these variables is set in the terminal environment, an exception is raised — even if all relevant environment variables have the same value.

The setting can also be set via `meltano config set` using either the canonical name or any alias:

```bash
# The canonical name
meltano config set my-custom-tap my_custom_tap_username some_value

# Alias 1
meltano config set my-custom-tap custom_tap_username some_value

# Alias 2
meltano config set my-custom-tap username some_value
```

To see what name or alias a setting's value derives from:

```shell
$ export MY_CUSTOM_TAP_USERNAME=some_username
$ meltano config list my-custom-tap
2024-06-22T10:00:00Z [info     ] Environment 'dev' is active
password [env: MY_CUSTOM_TAP_PASSWORD] current value: (redacted) (from the MY_CUSTOM_TAP_PASSWORD variable in `.env`)
my_custom_tap_username [env: MY_CUSTOM_TAP_MY_CUSTOM_TAP_USERNAME, MY_CUSTOM_TAP_CUSTOM_TAP_USERNAME, MY_CUSTOM_TAP_USERNAME] current value: 'some_username' (from the MY_CUSTOM_TAP_USERNAME variable in the environment)
```

If a setting's value is set via multiple environment variables, the error lists them:

```shell
$ export MY_CUSTOM_TAP_USERNAME=some_username
$ export MY_CUSTOM_TAP_CUSTOM_TAP_USERNAME=some_username
$ meltano config print my-custom-tap
Setting value set via multiple environment variables: ['MY_CUSTOM_TAP_CUSTOM_TAP_USERNAME', 'MY_CUSTOM_TAP_USERNAME']
```

If the values differ, the error also lists what the values are:

```shell
$ export MY_CUSTOM_TAP_USERNAME=some_username
$ export MY_CUSTOM_TAP_CUSTOM_TAP_USERNAME=some_other_username
$ meltano config print my-custom-tap
Conflicting values for setting found in: ['MY_CUSTOM_TAP_CUSTOM_TAP_USERNAME', 'MY_CUSTOM_TAP_USERNAME']
```

#### Expansion in setting values

Inside the values of settings in `meltano.yml`, environment variables can be referenced to dynamically adapt a plugin's configuration to the environment it's run in, specific properties of your project, or the plugins it's run with inside a `meltano run` pipeline.

##### Available plugin environment variables

The following variables can be referenced from any setting:

- Those specified in the execution environment
- Those set in your project's `.env` file
- `MELTANO_PROJECT_ROOT`: Absolute path to the current project directory, e.g. `/home/meltano-projects/demo-project`

Additionally, the following can be referenced from plugin settings (as opposed to Meltano settings):

- `MELTANO_<SETTING_NAME>`: Variables describing Meltano's current configuration, discoverable using `meltano config print --format=env meltano`
- `MELTANO_<PLUGIN_TYPE>_NAME`: The plugin's `name`, e.g. `MELTANO_EXTRACTOR_NAME` as `tap-gitlab` for extractor `tap-gitlab`
- `MELTANO_<PLUGIN_TYPE>_NAMESPACE`: The plugin's `namespace`, e.g. `MELTANO_EXTRACTOR_NAMESPACE` as `tap_gitlab` for extractor `tap-gitlab`

When running a `meltano el` pipeline, additional pipeline environment variables are available to loaders and transformers that describe the extractor and loader they're run with. When a plugin is invoked outside a pipeline context, these variables are unset and expand to empty strings.

Inside plugin extras, additional variables describing the plugin's current configuration are available, discoverable using `meltano config print --format=env <plugin>`. Generic `MELTANO_<PLUGIN_TYPE_VERB>_<SETTING_NAME>` variables can be used when the plugin name isn't known, e.g. `MELTANO_LOAD_SCHEMA` for a loader's `schema` setting.

##### How to use

Inside plugin `config` objects in `meltano.yml`, reference these variables using standard variable expansion syntax, `$VAR` (as a single word) or `${VAR}` (inside a word):

```yaml
extractors:
- name: tap-example
  config:
    simple_setting: $MELTANO_EXTRACTOR_NAME
    multiple_words: $MELTANO_EXTRACTOR_NAMESPACE foo
    part_of_a_path: $MELTANO_PROJECT_ROOT/example.txt
    inside_a_word: ${MELTANO_EXTRACTOR_NAMESPACE}_foo
```

> Values with a `$` character that are not intended to be expanded should be escaped with a backslash (`\$`), e.g. `\$VAR`:
>
> ```yaml
> extractors:
> - name: tap-example
>   config:
>     special_character_setting: MY_$VAR
> ```

#### Accessing from plugins

When Meltano invokes a plugin's executable as part of `meltano run` or `meltano invoke`, it populates the environment with the same variables that can be referenced from settings, as well as those describing the plugin's current configuration (including extras), as discoverable using `meltano config print --format=env <plugin>`.

These can be accessed from inside the plugin using the standard library mechanism, e.g. Python's `os.environ`.

Within a Meltano environment, environment variables can be specified using the `env` key:

```yml
environments:
- name: dev
  env:
    AN_ENVIRONMENT_VARIABLE: dev
```

Any plugins run in that Meltano environment will have the provided environment variables populated into the plugin's environment.

### Multiple plugin configurations

Every plugin in your project has its own configuration, but you can use plugin inheritance to define multiple plugins that use the same package but have their own configuration:

```yml
plugins:
  extractors:
  - name: tap-google-analytics
    variant: meltano
    config:
      key_file_location: client_secrets.json
      start_date: "2020-10-01T00:00:00Z"
  - name: tap-ga--view-foo
    inherit_from: tap-google-analytics
    config:
      # `key_file_location` and `start_date` are inherited
      view_id: 123456
  - name: tap-ga--view-bar
    inherit_from: tap-google-analytics
    config:
      # `key_file_location` is inherited
      start_date: "2020-12-01T00:00:00Z" # `start_date` is overridden
      view_id: 789012
```

Here, `tap-ga--view-foo` and `tap-ga--view-bar` are separate plugins that inherit their base plugin description (describing the package) and configuration (where not overridden) from `tap-google-analytics`, which itself shadows the discoverable plugin with the same name.

If there's no need for the different plugins to inherit any common configuration, they can directly inherit from the discoverable plugin instead, without an intermediary plugin:

```yml
plugins:
  extractors:
  - name: tap-postgres--billing
    inherit_from: tap-postgres
    config:
      host: one.postgres.example.com
      user: billing_user
      dbname: billing_db
  - name: tap-postgres--events
    inherit_from: tap-postgres
    config:
      host: two.postgres.example.com
      user: events_user
      dbname: events_db
```

To configure `tap-postgres`'s `password` setting, you'd typically set `TAP_POSTGRES_PASSWORD`, but that won't work here since it wouldn't be clear which plugin the password was intended for. Instead, both plugins get their own unique environment variables with prefixes derived from their names: `TAP_POSTGRES__BILLING_PASSWORD` and `TAP_POSTGRES__EVENTS_PASSWORD` (as `meltano config list <name>` would tell you).

### Custom settings

Meltano tracks the settings a plugin supports using `settings` metadata, listing them via `meltano config list <plugin>`.

If a plugin supports a setting not yet known to Meltano (perhaps added after the `settings` metadata was specified), you don't need to modify the `settings` metadata to use it. Instead, define a custom setting by adding the setting name (key) to your plugin's `config` object in `meltano.yml` with the desired value (or `null`), either by manually editing the file or using `meltano config set <plugin> <key> <value>`:

```bash
meltano config set tap-example custom_setting value
```

```yaml
extractors:
- name: tap-example
  config:
    known_setting: value
    custom_setting: value
```

As long as the custom setting exists in `meltano.yml`, it behaves and can be interacted with like any regular setting: it shows up in `meltano config list <plugin>` and `meltano config print <plugin>`, and its value can be overridden using an environment variable:

```bash
export TAP_EXAMPLE_CUSTOM_SETTING=overridden_value
```

### Plugin extras

Plugin extras are additional configuration options specific to the type of plugin (e.g. all extractors) that are handled by Meltano instead of the plugin itself.

Meltano currently knows these extras for these plugin types:

- Extractors
  - `catalog`
  - `load_schema`
  - `metadata`
  - `schema`
  - `select`
  - `select_filter`
  - `state`
- Loaders
  - `dialect`
- Transforms
  - `package_name`
  - `vars`
- File bundles
  - `update`

The values of these extras are stored in `meltano.yml` among the plugin's other properties, _outside_ the `config` object:

```yaml
extractors:
- name: tap-example
  config:
    # Configuration goes here!
    example_setting: value
  # Extras go here!
  example_extra: value
```

These extras can be thought of and interacted with as a special kind of setting — environment variables and `meltano config` can be used to manage them.

### Configuration testing

The configuration of a plugin can be tested using `meltano config test <plugin>`.

> Configuration testing is only supported for extractor plugins currently.

## User YAML Configuration

Meltano allows users to customize YAML formatting preferences (indentation, spacing) through a user configuration file, separate from the project's `meltano.yml`.

### Configuration file location

Stored in a platform-specific configuration directory:

- **Linux**: `$XDG_CONFIG_HOME/meltano/config.yml` (typically `~/.config/meltano/config.yml`)
- **macOS**: `~/Library/Application Support/meltano/config.yml`
- **Windows**: `%APPDATA%\meltano\config.yml`

The location respects the `XDG_CONFIG_HOME` environment variable on Linux when set.

### Creating the configuration file

The configuration directory and file are created automatically when Meltano first needs to read user configuration. You can also create them manually:

```bash
# Create the directory
mkdir -p ~/.config/meltano  # Linux
mkdir -p "~/Library/Application Support/meltano"  # macOS

# Create the config file
touch ~/.config/meltano/config.yml  # Linux
touch "~/Library/Application Support/meltano/config.yml"  # macOS
```

### Configuration format

```yaml
yaml:
  indent: 4
  block_seq_indent: 2
  sequence_dash_offset: 2
```

### Available settings

- `indent` (int): Base indentation level for mappings (default: 2, minimum: 1)
- `block_seq_indent` (int): Additional indentation for block sequences (default: 0, minimum: 0)
- `sequence_dash_offset` (int): Offset for sequence dashes (default: max(0, indent-2), minimum: 0)

**Standard 2-space indentation (default):**
```yaml
yaml:
  indent: 2
  block_seq_indent: 0
  sequence_dash_offset: 0
```

**4-space indentation with block sequence indentation:**
```yaml
yaml:
  indent: 4
  block_seq_indent: 2
  sequence_dash_offset: 2
```

### How it works

When Meltano writes YAML files (like `meltano.yml`), it applies these user configuration settings to control formatting:

- **indent**: Controls how much mapping keys are indented from their parent
- **block_seq_indent**: Additional indentation for sequence items beyond the base indent
- **sequence_dash_offset**: How far sequence dashes (`-`) are offset from the left margin

If invalid values are provided, Meltano logs a warning and falls back to defaults: negative `indent` values default to 2, negative `block_seq_indent` values default to 0.

### Disabling user configuration

Set `MELTANO_DISABLE_USER_YAML_CONFIG` to any truthy value (`1`, `true`, `yes`, `on`) to disable user configuration and force Meltano to use default YAML formatting settings:

```bash
export MELTANO_DISABLE_USER_YAML_CONFIG=true
```
