# Transformation and Orchestration

How Meltano integrates dbt for data transformation, and how to schedule and orchestrate pipelines using Meltano's scheduling primitives and Apache Airflow.

## Transformation with dbt

Transformations in Meltano are implemented using dbt. All Meltano generated projects have a `transform/` directory, which is the default location for your dbt configuration, models, packages, etc. After installing a dbt plugin, run an `initialize` command to automatically populate the contents of that directory.

> If you already have an existing dbt project you'd like to migrate to Meltano, see `migration-guides.md` for the existing dbt project guide.

### Adapter-Specific dbt Transformation

In alignment with dbt's own documentation, Meltano supports adapter-specific installations of dbt. See MeltanoHub for a list of all the supported adapters (e.g. Snowflake, Postgres, Redshift, BigQuery, DuckDB, etc.). If you're interested in another adapter, consider contributing its definition to MeltanoHub.

#### Install dbt

```bash
# install adapter-specific dbt, e.g. for snowflake
# Simplified syntax - plugin type is automatically detected
meltano add dbt-snowflake  # Automatically detected as utility

# Explicit plugin type for disambiguation:
# meltano add --plugin-type utility dbt-snowflake
```

After dbt is installed, configure it using `config` CLI commands, Meltano environments, or environment variables:

```bash
# list available settings
meltano config list dbt-snowflake

# configure the `dev` environment interactively
meltano --environment=dev config dbt-snowflake set --interactive

# configure the `prod` environment interactively
meltano --environment=prod config dbt-snowflake set --interactive
```

#### Running dbt in Meltano

There are two ways to run dbt utility plugins: in a pipeline using `run`, or standalone with arguments using `invoke`.

##### Running dbt as part of a pipeline

```bash
# run a complete ELT pipeline using the `dev` environment config
meltano --environment=dev run tap-gitlab target-snowflake dbt-snowflake:run
```

To run a subset of your dbt project, define a plugin command with your desired dbt selection filters:

```yaml
# meltano.yml
plugins:
  utilities:
    - name: dbt-snowflake
      commands:
        my_models:
          args: run --select +my_model_name
          description: Run dbt, selecting model `my_model_name` and all upstream models. Read more about the dbt node selection syntax at https://docs.getdbt.com/reference/node-selection/syntax
```

Execute as:

```bash
meltano --environment=dev run tap-gitlab target-snowflake dbt-snowflake:my_models
```

##### Invoking dbt directly

```bash
# run your entire dbt project
meltano invoke dbt-snowflake run

# run with node selection criteria
meltano invoke dbt-snowflake run --select +my_model_name

# run with a command specified in meltano.yml
meltano invoke dbt-snowflake:my_models
```

### dbt Installation and Configuration (Transformer Plugin Type — classic)

> These instructions are the classic way of installing and running dbt as a `transformer` plugin type. Users can still install dbt this way, but Meltano prioritizes dbt `utility` plugin types for new and existing users. The `elt` command does not support `utility` dbt plugins, so continue using a `transformer` if you prefer `elt` over `run`.

```bash
meltano add transformer dbt-<adapter-name>

# For example:
meltano add transformer dbt-snowflake
```

### dbt Installation and Configuration (Classic, non-adapter-specific)

> These instructions are also the classic way and are prioritized less than dbt utility plugin types.

```bash
meltano add transformer dbt
```

After dbt is installed, change the default configuration using environment variables or `config` CLI commands:

```bash
meltano config set dbt target <target>

# For example:
meltano config set dbt target postgres
```

### Working with Transform Plugins

> **WARNING**: Transform plugins are currently de-prioritized by the Meltano project due to the difficulty of maintaining them at scale. Users can still install and maintain them, but many have grown outdated and unmaintained. Some users install existing transform plugins as a starting point then customize them for their own transformations.

`Transform` plugins are dbt packages that reside in their own repositories. When a transform is added to a project, it's added as a dbt package in `transform/packages.yml`, enabled in `transform/dbt_project.yml`, and loaded the next time dbt runs.

You do not have to use `transform` plugin packages to use dbt — many teams instead create their own custom transformations.

#### Configuring Transform Plugins

Transform plugins may have additional configuration options in `meltano.yml`. For example, the `tap-gitlab` dbt package requires three variables used for finding the tables where raw data was loaded during Extract-Load:

```yml
transforms:
- name: tap-gitlab
  pip_url: https://gitlab.com/meltano/dbt-tap-gitlab.git
  vars:
    entry_table: "{{ env_var('PG_SCHEMA') }}.entry"
    generationmix_table: "{{ env_var('PG_SCHEMA') }}.generationmix"
    region_table: "{{ env_var('PG_SCHEMA') }}.region"
```

Alternatively, set values directly:

```yml
transforms:
  - name: tap-gitlab
    pip_url: https://gitlab.com/meltano/dbt-tap-gitlab.git
    vars:
      entry_table: "my_raw_schema.entry"
      generationmix_table: "my_raw_schema.generationmix"
      region_table: "my_raw_schema.region"
```

Whenever Meltano runs a new transformation, `transform/dbt_project.yml` is updated using the values provided in `meltano.yml`.

#### Running a Transform in Meltano

The two main ways to run dbt transforms: inline with your ELT pipeline using `--transform run`, or decoupled using `invoke dbt:run`.

##### Transform in your ELT pipeline

> **WARNING**: `meltano elt` is deprecated and will eventually be removed. Use `meltano run` for the most up-to-date way to run data pipelines.

When `meltano elt` runs with `--transform run`, Meltano uses the convention that the transform has the same namespace as the extractor, except in snake_case (`tap-gitlab` -> `tap_gitlab`).

```bash
meltano elt <tap> <target> --transform run

# For example:
meltano elt tap-gitlab target-postgres --transform run
```

After Extract and Load complete, the dbt transform in `/transform/models/tap_gitlab/` runs. Under the hood `--transform run` tells Meltano to run multiple dbt commands: first `dbt deps` to install dependencies, then `dbt run --models <models>`. The `<models>` argument is populated using the Meltano transform `models` setting.

This method lets Meltano make assumptions about the appropriate dbt configuration. Based on the target loader used, Meltano defaults your dbt transform `target` setting to the correct SQL dialect (e.g. Snowflake, Postgres, etc.).

Starting with Meltano v3, the default `source_schema` value of `$MELTANO_LOAD__TARGET_SCHEMA` stops working since the target extra was removed. Fix by setting `source_schema` to the appropriate environment variable for your target (e.g. `$MELTANO_LOAD__DEFAULT_TARGET_SCHEMA` for Postgres).

##### Transform directly

dbt transforms can be executed directly using `invoke`, decoupling dbt transformations from ELT pipelines. Useful if you want to replicate data from many sources before running a set of dbt models that blend all of them together, or if multiple models reference the same source data but are refreshed on different cadences.

```bash
meltano invoke dbt:<command>

# For example:
meltano invoke dbt:run --models tap_gitlab.*
```

This runs all dbt models in `/transform/models/tap_gitlab/`. The downside versus running in a pipeline is that Meltano can't infer as much about how dbt should run, so more settings might need to be explicitly set: target dialect `DBT_TARGET`, target schema `DBT_TARGET_SCHEMA`, and models `DBT_MODELS`.

#### Adding a Transform to your Meltano Project

Once the dbt transformer is installed, `/transform` is populated with dbt artifacts. If using `--transform run` in an ELT pipeline, remember Meltano uses the convention that the transform has the same namespace as the extractor in snake_case. Write dbt models in the appropriate `/transform/models/<tap_name>/` directory.

Another common option is installing your dbt project as a package from a separate git repository (see dbt package management docs). Add a `/transform/packages.yml` file:

```yaml
packages:
  - git: https://gitlab.com/your_repo/your-dbt-project.git
    revision: 1.0.0
```

If calling dbt directly using `invoke`, first run `meltano invoke dbt:deps` to install package dependencies. Using `--transform=run` in your pipeline handles this automatically.

## Orchestration

Most data pipelines aren't run just once, but over and over again, to make sure additions and changes in the source eventually make their way to the destination. Meltano supports scheduled pipelines that can be orchestrated using Apache Airflow.

When a new pipeline schedule is created using the CLI, a DAG is automatically created in Airflow as well, representing "a collection of all the tasks you want to run, organized in a way that reflects their relationships and dependencies."

### Create a Schedule

#### Scheduling predefined jobs

First define the pipeline as a job within your project, then schedule it with `meltano schedule add`:

```bash
# Define a job
meltano job add tap-gitlab-to-target-postgres-with-dbt --tasks "tap-gitlab target-postgres dbt-postgres:run"

# Schedule the job
meltano schedule add daily-gitlab-load --job tap-gitlab-to-target-postgres-with-dbt --interval '@daily'
```

This adds the following schedule to `meltano.yml`:

```yaml
schedules:
- name: daily-gitlab-load
  interval: '@daily'
  job: tap-gitlab-to-target-postgres-with-dbt
```

Supply schedule-specific environment variables via the `env` key:

```yaml
schedules:
- name: daily-gitlab-load
  interval: '@daily'
  job: tap-gitlab-to-target-postgres-with-dbt
  env:
    SCHEDULE_SPECIFIC_ENV_VAR: schedule_specific_value
```

### Run a schedule manually

```bash
meltano schedule run daily-gitlab-load
```

### Installing Airflow

While Meltano's CLI can define pipeline schedules, actually executing them is the orchestrator's responsibility. From inside your Meltano project:

```bash
# Simplified syntax - plugin type is automatically detected
meltano add airflow  # Automatically detected as utility

# Explicit plugin type for disambiguation:
# meltano add --plugin-type utility airflow

# Deprecated positional syntax:
# meltano add utility airflow

meltano invoke airflow:initialize
meltano invoke airflow users create -u admin@localhost -p password --role Admin -e admin@localhost -f admin -l admin
```

This adds the default DAG generator to your project and makes Airflow available via `meltano invoke`. See the Airflow docs page on MeltanoHub for more details.

#### Using an existing Airflow installation

You can use the Meltano DAG generator with an existing Airflow installation, as long as `MELTANO_PROJECT_ROOT` is set to point at your Meltano project.

All `meltano invoke airflow ...` does is populate `MELTANO_PROJECT_ROOT`, set Airflow's `core.dags_folder` setting to `$MELTANO_PROJECT_ROOT/orchestrate/dags` (where the DAG generator lives by default), and invoke the `airflow` executable with the provided arguments.

Add the Meltano DAG generator to your project without also installing the Airflow orchestrator plugin, by adding the `airflow` file bundle:

```bash
meltano add files files-airflow
```

Then copy the DAG generator into your Airflow installation's `dags_folder`, or reconfigure it to look in your project's `orchestrate/dags` directory instead.

This setup assumes you'll use `meltano schedule` to schedule your `meltano el` pipelines, since the DAG generator iterates over the result of `meltano schedule list --format=json` and creates DAGs for each. You can also create your own Airflow DAGs for any pipeline using `BashOperator` with the `meltano el` command, or `DockerOperator` with a project-specific Docker image.

### Starting the Airflow scheduler

```bash
meltano invoke airflow scheduler
```

Airflow will now run your pipelines on a schedule as long as the scheduler is running.

### Using Airflow directly

You're free to interact with Airflow directly through its own UI:

```bash
meltano invoke airflow webserver
```

By default, you'll see Meltano's pipeline DAGs, created automatically using the dynamic DAG generator included with every Meltano project, located at `orchestrate/dags/meltano.py`.

You can use the bundled Airflow with custom DAGs by putting them inside `orchestrate/dags`, where they'll be picked up automatically.

Meltano's use of Airflow will be unaffected by other usage of Airflow as long as `orchestrate/dags/meltano.py` remains untouched and pipelines are managed through the dedicated interface.

#### Other things you can do with Airflow

`meltano invoke` gives you raw access to the underlying plugin after any configuration hooks.

```bash
# View 'meltano' dags:
meltano invoke airflow dags list

# Manually trigger a task to run:
meltano invoke airflow tasks run --raw meltano extract_load $(date -I)

# Start the Airflow UI: (will start in a separate browser)
meltano invoke airflow webserver

# Start the Airflow scheduler, enabling job processing:
meltano invoke airflow scheduler

# Trigger a dag run:
meltano invoke airflow dags trigger meltano
```

Airflow is a full-featured orchestrator with many features currently outside Meltano's scope. Refer to the Airflow documentation for more in-depth knowledge.
