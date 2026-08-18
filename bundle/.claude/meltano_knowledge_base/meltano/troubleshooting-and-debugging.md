# Troubleshooting and Debugging

How to diagnose problems with Meltano pipelines and plugins, plus how to debug a custom Singer extractor in an IDE.

## Common Issues

**Problem: "Why do incremental runs produce duplicate data?"**

Singer takes an "at least once" approach to replication, so this might be intended behavior.

**Problem: "My runs take too long."**

Investigate performance issues systematically — check which streams are slow, whether replication is full-table vs incremental, and where time is being spent (source API vs target write).

## How to Debug Problems

### Log Level Debug

When troubleshooting, Meltano logs should be your first port of call.

If you have a failure using Meltano's execution commands (`invoke`, `elt`, `run`, or `test`) or experienced unexpected behavior, learn more about what's happening behind the scenes by setting Meltano's `cli.log_level` setting to debug, using the `MELTANO_CLI_LOG_LEVEL` environment variable or the `--log-level` CLI option:

```bash
# meltano config
meltano config set meltano cli log_level debug

# env
export MELTANO_CLI_LOG_LEVEL=debug

# command
meltano --log-level=debug <command> ...
```

In debug mode, Meltano logs additional information about the environment and arguments used to invoke your components (Singer taps and targets, dbt, Airflow, etc.), including paths to the generated config, catalog, state files, etc.

Example with `meltano run`:

```
$ meltano --log-level=debug run tap-gitlab target-jsonl
2023-02-01T17:17:43.308389Z [info     ] Environment 'dev' is active
2023-02-01T17:17:43.375158Z [debug    ] Creating engine '<meltano.core.project.Project object at 0x10d9ff5e0>@sqlite:////demo-project/.meltano/meltano.db'
2023-02-01T17:17:43.646112Z [debug    ] Found plugin parent            parent=tap-gitlab plugin=tap-gitlab source=lockfile
2023-02-01T17:17:43.650014Z [debug    ] found plugin in cli invocation plugin_name=tap-gitlab
2023-02-01T17:17:43.652873Z [debug    ] Found plugin parent            parent=target-jsonl plugin=target-jsonl source=lockfile
2023-02-01T17:17:43.656906Z [debug    ] found plugin in cli invocation plugin_name=target-jsonl
2023-02-01T17:17:43.657112Z [debug    ] head of set is extractor as expected block=<meltano.core.plugin.project_plugin.ProjectPlugin object at 0x1115be850>
2023-02-01T17:17:45.337292Z [debug    ] found block                    block_type=loaders index=1
2023-02-01T17:17:45.337455Z [debug    ] blocks                         idx=1 offset=0
2023-02-01T17:18:54.233065Z [debug    ] found ExtractLoadBlocks set    offset=0
2023-02-01T17:18:54.233220Z [debug    ] All ExtractLoadBlocks validated, starting execution.
2023-02-01T17:18:56.271112Z [debug    ] Created configuration at /home/.meltano/run/tap-gitlab/tap.54d0e4e3-eb71-4000-9138-47a25c8b3743.config.json
2023-02-01T17:18:56.271662Z [debug    ] Could not find tap.properties.json in /home/.meltano/extractors/tap-gitlab/tap.properties.json, skipping.
2023-02-01T17:18:56.272003Z [debug    ] Could not find tap.properties.cache_key in /home/.meltano/extractors/tap-gitlab/tap.properties.cache_key, skipping.
2023-02-01T17:18:56.272321Z [debug    ] Could not find state.json in /home/.meltano/extractors/tap-gitlab/state.json, skipping.
2023-02-01T17:18:56.355385Z [warning  ] No state was found, complete import.
...
```

### Isolate the Connector

If it's unclear which part of the pipeline is generating the problem, test the tap and target individually using `meltano invoke`, which runs the executable with any specified arguments.

```bash
meltano invoke <plugin> [PLUGIN_ARGS...]
```

It's usually easiest to pipe the raw output of the tap to a file to confirm the tap works, then pipe that file's contents to the target so the tap doesn't have to re-replicate the data:

```bash
meltano invoke tap-csv > output.json
cat output.json | meltano invoke target-postgres
```

### Validate Tap Capabilities

If the tap is not loading any streams, or doesn't appear to be respecting configured `select` rules, validate the tap's capabilities.

In prior versions of the Singer spec, `--properties` was used instead of `--catalog` for catalog files. If this is the case for a tap, ensure `properties` is set as a capability for the tap instead of `catalog`. Then `meltano el` will accept the catalog file and pass it to the tap using the appropriate flag.

### Testing Specific Failing Streams

When extracting several streams with a single tap using the `elt` command, it can be hard to debug a single failing stream. It's useful to run the tap with just that single stream selected.

Instead of duplicating the extractor in `meltano.yml`, run `meltano el` with the `--select` flag. This runs the pipeline with just that stream selected.

You can also have `meltano invoke` select an individual stream by setting the `select_filter` extra as an environment variable:

```bash
export <TAP_NAME>__SELECT_FILTER='["<your_stream>"]'
```

### Incremental Replication Not Running as Expected

If using a custom tap, ensure it declares the `state` capability.

If using `meltano run`, be aware the state ID is generated using extractor name + loader name + environment name. If you switched environments, you might not have the state you were expecting.

If using `meltano el` and expecting incremental replication but getting a full sync, ensure you're passing a State ID via the `--state-id` flag.

### Dump Files Generated by Running Meltano Commands to STDOUT

The `--dump` flag can be passed to `meltano invoke` and `meltano el` to dump the content of a pipeline-specific generated file to STDOUT instead of actually running the pipeline (not yet supported for `meltano run`).

This aids in debugging extractor catalog generation, incremental replication state lookup, and pipeline environment variables.

Supported values:

- **catalog**: Dump the extractor catalog file that would be passed to the tap's executable using `--catalog`.
- **state**: Dump the extractor state file that would be passed to the tap's executable using `--state`.
- **extractor-config**: Dump the extractor config file that would be passed to the tap's executable using `--config`.
- **loader-config**: Dump the loader config file that would be passed to the target's executable using `--config`.

The dumped content can be redirected to a file using `>`, e.g. `meltano el ... --dump=state > state.json`.

Examples:

```bash
meltano el tap-gitlab target-postgres --transform=run --state-id=gitlab-to-postgres

meltano el tap-gitlab target-postgres --state-id=gitlab-to-postgres --full-refresh

meltano el tap-gitlab target-postgres --catalog extract/tap-gitlab.catalog.json
meltano el tap-gitlab target-postgres --state extract/tap-gitlab.state.json

meltano el tap-gitlab target-postgres --select commits
meltano el tap-gitlab target-postgres --exclude project_members

meltano el tap-gitlab target-postgres --state-id=gitlab-to-postgres --dump=state > extract/tap-gitlab.state.json
```

### Alternatives to `meltano run --dump`

The `--dump` flag is not supported with `meltano run`, but you can achieve the same outcomes using other commands.

**Dumping State** — instead of `meltano run ... --dump=state`:

```bash
meltano state get <STATE_ID>
```

**Dumping Extractor Configuration** — instead of `meltano run ... --dump=extractor-config`:

```bash
meltano config list <EXTRACTOR_NAME>

# Alternatively:
meltano invoke --dump=config <EXTRACTOR_NAME>
```

**Dumping Loader Configuration** — instead of `meltano run ... --dump=loader-config`:

```bash
meltano config list <LOADER_NAME>
```

**Dumping Catalog** — instead of `meltano run ... --dump=catalog`:

```bash
meltano invoke --dump=catalog <EXTRACTOR_NAME>
```

### Meltano UI

Early versions of Meltano promoted a simple UI for setting up basic pipelines and viewing basic logs. Due to a refocusing of the product on the CLI, the UI was deprioritized. For interactive plugin configuration, use the `--interactive` config option in the CLI instead.

#### Limitations & Capabilities of the Deprecated UI

The UI is not compatible with many newer Meltano features.

The UI **does** work with:
- Schedules based on the `elt` command (`meltano schedule add <schedule_name> --extractor <tap> --loader <target> --transform ...`)

The UI does **not** work with:
- Schedules based on jobs (`meltano schedule add <schedule_name> --job <job>`)
- Environments

#### Replacing UI functionality

If using Airflow or Dagster as your orchestrator, their webserver UI can serve as a replacement for many Meltano UI use cases. For Airflow, see the "Airflow orchestrator" section of the "Deployment in Production" guide (`deployment-and-operations.md`) for details on running the webserver. From there you can view all DAGs, and access Meltano logs for a specific task instance in the Audit Log.

### No Plugin Settings Defined

To configure a plugin that doesn't already have settings defined, first add a `settings:` entry under the plugin definition (consult the plugin's documentation to determine what settings are available). See "Overriding discoverable plugin properties" and "Custom settings" in `usage.md` for the relevant configuration mechanics.

After adding definitions for the plugin's settings, configure those settings as usual with the `--interactive` option in `meltano config`.

## Debug a Custom Extractor

### Add a main block in tap.py of your custom extractor

```python
if __name__ == "__main__":
    # TapCustomExtractor is the class name of your tap in tap.py
    TapCustomExtractor.cli()
```

### Create a local venv that your debugger can use

If you're using `uv`, a virtual environment is automatically created in the tap directory so your IDE can pick it up when debugging.

### What to put in VSCode launch.json

Add the following launch configuration to your project:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            // Replace tap_foobar below with the actual name of your custom extractors library
            "program": "${workspaceRoot}/tap_foobar/tap.py",
            "console": "integratedTerminal",
            "args": ["--config", ".secrets/config.json"],
            "env": { "PYTHONPATH": "${workspaceRoot}"},
            // Change this to false if you wish to debug and add breakpoints outside of your code e.g. the singer-sdk package
            "justMyCode": true
        }
    ]
}
```

### Create a config.json to use when debugging

The launch.json above specifies the location of this config as `.secrets/config.json`. Feel free to change this, but ensure the config has all the required fields for your custom extractor to run successfully.

### Happy Debugging

You should now be able to add breakpoints where needed and run the debugger.
