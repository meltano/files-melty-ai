# PipelineML

Reference for the pipeline definition file (`pipelines/*.yml`) used to orchestrate data actions in a Meltano Cloud workspace as code, including environment configuration and custom scripts.

## Overview

Use the pipeline YAML to orchestrate data actions in your workspace as code. Pipeline definitions are stored in YAML file format.

### Example: `pipelines/report_pipeline.yml`

```yaml
version: pipelines/v0.1
type: WORKFLOW
data_components:
- notebook
- sendgrid
actions:
- notebook:run-convert
- sendgrid:send
properties:
  notebook.path: notebook/data_quality_report.ipynb
timeout: 1500
max_retries: 3
schedule: 0 0 0 * * 0
triggered_by:
- other-pipeline
- deploy
```

### Key Fields

| Path | JSON Type | Description |
|---|---|---|
| `version` | `string` | The version identifies this artifact type. |
| `type` | `string` | `INGESTION` or `WORKFLOW` (any case). See [Pipeline types](#pipeline-types). |
| `data_components` | `string[]` | The meltano.yml data component name. |
| `actions` | `string[]` | The Meltano tasks that will be run as defined in your meltano.yml or Plugins. |
| `inline_script` | `string` | Custom Bash script. Overrides `actions` if supplied. |
| `timeout` | `number` | A timeout value in seconds that prevents pipelines from running for too long. A pipeline running longer than the timeout setting is automatically stopped. |
| `max_retries` | `number` | The maximum number of retries to attempt for a job ending with `ERROR`. |
| `properties` | `object` | A map of properties, with Data Component name and setting as the key and the value e.g. `data-component-name.setting=value`, that configures the pipeline environment. |
| `schedule` | `string` | The automated schedule for this pipeline, in a standard cron format with seconds. E.g. `0 0 9-17 * * MON-FRI` runs on the hour nine-to-five weekdays. |
| `triggered_by` | `string[]` | Pipelines or workspace tasks that will trigger the pipeline on successful completion. Supported values for workspace tasks (case-insensitive): `deploy` — workspace deployment. |

Further reading: Pipelines API resource (`/reference/cloud/api/resources/pipelines`).

### Pipeline types

Every pipeline is an **ingestion** or a **workflow**, set by `type:`.

- **`INGESTION`** moves data from one source into one warehouse: exactly one extractor, any mappers, and exactly one loader (a data store such as `Warehouse`). Nothing else: no dbt or other transformer, no utility, no `inline_script`, and no plugin commands (`dbt:run`, `x:y`) in `actions`.
- **`WORKFLOW`** is everything else: dbt, utilities, scripts, commands, several sources.

dbt never goes in an ingestion. Put it in a workflow that lists the ingestion under `triggered_by`, so it runs after each sync:

```yaml
# pipelines/orders.yml
version: pipelines/v0.1
type: INGESTION
data_components:
- tap-postgres
- Warehouse
schedule: 0 0 0 * * *
```

```yaml
# pipelines/orders-dbt.yml
version: pipelines/v0.1
type: WORKFLOW
data_components:
- dbt
actions:
- dbt:deps
- dbt:run
triggered_by:
- orders
```

Rules on deploy:

- **Always write `type:`.** A new file without it deploys as a `WORKFLOW`; for an existing pipeline, a missing `type:` keeps the type it already has.
- The only allowed change is `WORKFLOW` → `INGESTION`, in place (the pipeline keeps its sync state). An ingestion can't become a workflow; create a new pipeline instead.
- A file that breaks the ingestion rules (e.g. adds dbt), or names a type the pipeline can't take, still deploys, but as a **draft** that can't run until the file is fixed. The pipeline's problems say what to change.


---

## Environment

Pipelines have environments that are used to pass configuration to the underlying plugins they reference.

### Viewing Your Environment

You can see what environment a pipeline is running with by navigating to it, clicking the expand arrow, and choosing the Environment tab. This tab shows all settings being used for your data source, data store, and any other plugins you are using.

Some of these settings will be hidden with the value `***`, but when you copy and paste your environment (which you can do just by clicking anywhere in the environment window), these values will be shown.

### Default Environment

Your pipeline's environment by default will contain:

- Configuration values for all data-plugin settings set on the pipeline or referenced data components.
- `EXTRACTOR`, if referencing a data component backed by an extractor data plugin.
- `LOADER`, if referencing a data component/data store backed by a loader data plugin.
- `DBT_TARGET`, pertaining to a data store referenced by the pipeline, or the workspace default.
- `DBT_SOURCE_SCHEMA`, pertaining to a data store referenced by the pipeline, or the workspace default.
- `DBT_TARGET_SCHEMA`, pertaining to a data store referenced by the pipeline, or the workspace default.
- `MELTANO_STATE_BACKEND_URI`
- `MELTANO_ENVIRONMENT`

See Meltano's "Configuring settings" guide (`/guide/configuration#configuring-settings`) for more information on how Meltano handles plugin configuration from environment variables.

Details on the above variables:

- **`EXTRACTOR`, `LOADER`** — `name` of the extractor/loader data plugin referenced by a pipeline data component.
- **`DBT_TARGET`** — `namespace` of the loader data plugin referenced by a pipeline data store data component, or the workspace default data store.
- **`DBT_SOURCE_SCHEMA`, `DBT_TARGET_SCHEMA`** — Schema of the pipeline data store data component, or the workspace default data store.
- **`MELTANO_STATE_BACKEND_URI`** (`/reference/settings#state_backenduri`) — Defines where state for the pipeline is stored. By default, this points at the Postgres database provisioned for the workspace (if no other supported datastore is referenced by the pipeline). State is generally stored in a `meltano` schema, unless otherwise specified.
- **`MELTANO_ENVIRONMENT`** (`/concepts/environments#activation`) — The active Meltano environment, controlled by the workspace default environment.

### Editing Your Environment

You can add to or overwrite your environment variables by using a custom data import script (see Custom Scripts below).

In your custom data import script you can add new or overwrite existing environment variables with a single line:

```bash
export <NEW_OR_EXISTING_SETTING_NAME>=<NEW_VALUE>
```

### Further Reading (Environment)

- `MELTANO_STATE_BACKEND_URI`: `/reference/settings/#state_backenduri`
- `MELTANO_ENVIRONMENT`: `/concepts/environments/#activation`

---

## Custom Scripts

Custom scripts can be used in pipelines by choosing "Custom Bash Script" from the "Actions" tab when editing your pipeline in Meltano Cloud, or by defining `inline_script` in your pipeline YAML file (see the `inline_script` field above).

### Basics

Custom scripts are Bash scripts that generally invoke Meltano commands. As with the default environment, you can also control the pipeline environment in these scripts.

When you provide a script to a pipeline, Meltano Cloud will still add your plugins' properties to the pipeline environment. Other than that, you are now in complete control of the environment, installation of plugins, and execution of your pipeline.

### Recommendations

#### Minimal Script

The following runs an extract-load to sync data from `<tap>` to `<target>`. For a pipeline with data components referencing this tap and target only, this script is identical to what is run by default.

```bash
meltano run --state-id-suffix $PIPELINE_ID <tap> <target>
```

`--state-id-suffix $PIPELINE_ID` ensures state is unique to the pipeline for the given tap/target combination.

#### Using Meltano To Invoke Other Plugins

```bash
meltano invoke dbt deps
meltano invoke dbt run
```

By invoking other plugins through Meltano, you gain the benefit of Meltano taking base-level environment variables and passing them to these plugins to use. This isn't perfect in every case, but generally will get you around setting a lot of environment variables manually.

### Further Reading (Custom Scripts)

- Examples of custom scripts: https://github.com/Matatika/matatika-examples/tree/master/example_data_import_scripts
- Default pipeline run script: https://github.com/Matatika/matatika-examples/blob/master/example_data_import_scripts/default.sh
- Technical glossary (Custom data source): https://github.com/Matatika/matatika-examples/tree/master/matatika_technical_glossary#custom-data-source
