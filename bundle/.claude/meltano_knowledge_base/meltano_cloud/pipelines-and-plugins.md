# Pipelines and Plugins

How to manage plugins, import data, transform it with dbt, and automate more advanced pipeline workflows in Meltano Cloud.

## Plugins

Access plugins from the left navigation bar by selecting **Workspace → Plugins**. This section lets you manage all Singer.io taps, dbt transforms, and Matatika datasets that power your data pipelines.

The Plugins page is organized into three tabs: **Installed**, **Available**, and **Custom**.

### Installed

View and manage all plugins currently installed in your workspace.

- A search bar at the top lets you quickly find any installed plugin by name.
- Each installed plugin card displays the plugin name, type, and variant.
- **Add to Pipeline** — Click the **Pipeline** button on any plugin card to add it directly to a pipeline without leaving this page.
- **Delete a Plugin** — Click the three-dot menu (⋮) on a plugin card and select **Delete** to remove it from your workspace.

### Available

Browse and install from the full library of plugins ready for use.

- A search bar lets you search across 550+ available plugins.
- Each plugin card shows the plugin name, type, and a brief description.
- **Install a Plugin** — Click the **Install** button on any plugin card to add it to your workspace. It will then appear under the Installed tab.
- **Delete a Plugin** — Click the three-dot menu (⋮) on a plugin card and select **Delete** if you need to remove it.

### Custom

Add your own custom data sources to the workspace by uploading a Meltano `discovery.yml` file.

Your discovery file describes all the Singer.io taps, dbt transforms, and Matatika datasets used to import, transform, and visualise your data.

- Click the **Add** button to open the custom plugin modal.
- In the modal, you can:
  - **Upload a file** — Select and upload your `discovery.yml` directly.
  - **Write YAML manually** — Type or paste your YAML content directly into the editor box.
  - **Reset** — Clear the editor and start over using the reset option.
- Click **Cancel** at any time to close the modal without saving.

Need help with discovery files? Browse examples in the [Meltano Documentation](https://docs.meltano.com/getting-started/).

### Choosing a plugin variant

Many taps and targets are available in more than one variant (e.g. `meltanolabs`,
`transferwise`, a vendor's own variant). When multiple variants exist for the same
plugin, prefer the **`meltanolabs`** or **`matatika`** variants — these are maintained by the MeltanoLabs
GitHub org and are the best-supported and most actively maintained options across the
plugin ecosystem. Only choose a different variant if `meltanolabs` / `matatika` doesn't exist for that
plugin, or if the workspace has a specific, documented reason to use another one (check
`.claude/workspace_knowledge_base/plugins.md` for any such override before installing).

---

## Importing data

This covers everything needed to get data flowing into your workspace: installing a plugin, setting up a data import pipeline, running an import locally, and connecting a fully custom data source.

### Adding a plugin to your workspace

**Time required: 5 minutes**

Prerequisites: access to a workspace, admin permissions for that workspace.

Plugins are the building blocks of data imports in Meltano. An extractor plugin pulls data from a source (such as Google Analytics, Shopify, or a spreadsheet), and a loader plugin writes it to your data store. Before you can create a pipeline, the relevant plugin needs to be installed in your workspace.

Steps:

1. In your workspace, click the **Lab** button in the left menu.
2. Select **Plugins** and open the **Available** tab.
3. Find or search for the plugin you want to install.
4. Click **Install**.

The plugin is now added to your workspace and committed to its backing repository.

From here, your next step depends on what kind of plugin you installed:

- If you installed a data source plugin (an extractor), continue to Create a Data Import Pipeline below.
- If you installed a different plugin type or want full control over execution, see Create a Custom Pipeline further below.

Can't find the plugin you need? If your data source is not listed in the Available tab, you can bring in your own — see Adding a Custom Data Source below.

### Create a data import pipeline

**Time required: 5 minutes**

Prerequisites: access to a workspace, admin permissions for that workspace, a data source plugin already installed.

A data import pipeline connects an extractor to your data store and runs it on a schedule you define. Each data source has its own required settings, and guidance for each one is shown on the right side of the screen as you configure it.

Steps:

1. In your workspace, click **Lab** in the left menu, then go to **Plugins** and open the **Available** tab.
2. Find or search for your data source and click **Install**. You will be moved to the **Installed** tab.
3. Click the **+ Pipeline** button next to your chosen data source plugin.
4. In the **Name** field at the top, give your pipeline a clear, recognisable name.
5. Expand the settings sections and fill in all required fields, which are marked with an asterisk (`*`). Some sources use a **Connect to Google** button instead.
6. In the **Clean, transform and organise** section, choose whether to use the default import actions or supply your own custom actions or script.
7. In the **Automate your import** section, set how often the pipeline should run. You can choose from preset schedules or define a custom one using cron syntax.
8. Click **Save**. A confirmation bar will appear at the top of the screen.
9. Navigate to the **Pipelines** screen. For the next one to two minutes a config job will run to set up your pipeline and commit the changes to your workspace repository.
10. Once the config job has finished, you can run the pipeline manually or leave it to run on its schedule.

Note: Do not attempt to run the pipeline while the config job is still in progress. Wait for it to complete before triggering a manual run.

### Running your data import locally

**Time required: 15 minutes**

Prerequisites: owner or admin access to the workspace containing the pipeline, Git installed, Python 3.8 or higher installed, Meltano installed (a virtual environment is recommended).

Every Meltano workspace is backed by a GitHub repository containing a Meltano project. You can clone that repository to your local machine and run any of your data import pipelines without using the cloud platform at all. This is useful for debugging, development, or simply running a pipeline from your own environment.

Setup:

1. In the Meltano app, switch to the workspace that contains the pipeline you want to run locally.
2. Navigate to **Settings** and copy the repository URL.
3. Clone the repository to your local machine:

```bash
git clone https://github.com/YourOrg/your-workspace
```

4. Change into the cloned directory and create a new `.env` file:

```bash
cd your-workspace
touch .env
```

5. Back in the Meltano app, go to **Lab**, then **Pipelines**, and expand the pipeline you want to run.
6. Open the **Environment** tab and click the `.env` text field to copy the environment configuration for that pipeline.
7. Paste the copied values into the `.env` file you created. It will look something like this:

```bash
TAP_EXAMPLE_CLIENT_ID=your-client-id
TAP_EXAMPLE_CLIENT_SECRET=your-client-secret
TAP_EXAMPLE_START_DATE=2022-01-01T00:00
TARGET_EXAMPLE_HOST=example.host.com
TARGET_EXAMPLE_PORT=1234
TARGET_EXAMPLE_DB=your-database
TARGET_EXAMPLE_SCHEMA=your-schema
TARGET_EXAMPLE_USERNAME=your-username
TARGET_EXAMPLE_PASSWORD=your-password
```

A working example of a locally configured workspace is available at the [Meltano examples repository](https://github.com/Matatika/matatika-examples/tree/master/example_local_data_import_workspace).

Running the pipeline (activate your virtual environment first, if using one):

1. Install the extractor:

```bash
meltano install extractor tap-example
```

2. Install the loader:

```bash
meltano install loader target-example
```

3. Run the pipeline:

```bash
meltano run tap-example target-example
```

Replace `tap-example` and `target-example` with the actual plugin names from your workspace configuration.

Finding your plugin names: they are visible in the pipeline settings in the Meltano app, and are also defined in the `meltano.yml` file in your cloned repository.

### Adding a custom data source

**Time required: 15 minutes**

Prerequisites: admin or owner access to the workspace you want to use.

If the data source you need is not available in the plugin catalogue, Meltano supports adding fully custom data sources using a plugin definition file. You can define your extractor, any related transforms, and file bundles (which contain pre-built datasets for visualisation) all in one step by pasting or uploading a YAML definition.

The example below walks through adding a custom version of `tap-spreadsheets-anywhere`, renamed to `tap-example-custom-data-source`, including an analyze file bundle that automatically publishes datasets to your workspace once the import runs.

#### Step 1 — Open the custom source importer

1. In your workspace, click the **Lab** button.
2. Go to the **Pipelines** page.
3. Click **+ Import**.
4. Select the **Custom** tab and click **Connect** on the Custom option.

#### Step 2 — Paste your plugin definition

In the popup window, paste your plugin definition YAML. The file can have any name but must follow the correct Meltano plugin YAML format.

For this example, use the following definition:

```yaml
extractors:
  - name: tap-example-custom-data-source
    variant: matatika
    namespace: tap_example_custom_data_source
    pip_url: git+https://github.com/ets/tap-spreadsheets-anywhere.git
    executable: tap-spreadsheets-anywhere
    capabilities:
      - catalog
      - discover
      - state
    settings:
      - name: tables
        kind: array
files:
  - name: analyze-example-custom-data-source
    variant: matatika
    namespace: tap_example_custom_data_source
    update:
      analyze/datasets/tap-example-custom-data-source: true
    pip_url: git+https://github.com/Matatika/analyze-example-custom-data-source.git
```

The `files` block adds an analyze bundle that shares the same namespace as the extractor. When Meltano sees a matching namespace during a data import config job, it automatically installs the bundle and publishes its datasets to your workspace so you can immediately visualise the imported data.

#### Step 3 — Configure the pipeline settings

After clicking **Next**, you will be on the pipeline settings screen:

1. Expand the **tap-example-custom-data-source** section.
2. For the **Tables** array field, paste the following to use a sample CSV file:

```json
[{
  "path": "https://raw.githubusercontent.com/Matatika/matatika-examples/master/example_adding_a_custom_data_source",
  "name": "imdb_top_20_films",
  "pattern": "imdb_top_20_films.csv",
  "start_date": "2021-01-01T00:00:00Z",
  "key_properties": ["rank"],
  "format": "csv"
}]
```

3. Leave Section 2 (Clean, transform and organise) on **Default** for this example.
4. Leave Section 3 (Automate your import) on **Manual** for this example.
5. Click **Save**.

#### Step 4 — Run the data import

After saving, a config job will start automatically on the Pipelines screen. This job adds your custom data source and its associated analyze bundle to the workspace repository. Once it completes:

1. Click the **Start job** button (solid arrow) next to your new pipeline to run the import.
2. When the job finishes, the datasets from the analyze bundle will be visible and populated in your workspace.

Note: The config job must complete before you attempt to run the data import. Running too early will result in an error.

---

## Transform data

**Time required: 15 minutes**

Prerequisites: completed the Setup your Development Environment guide, a workspace repository cloned to your local machine.

### Overview

A data transform is a layer of logic that reshapes one set of data into another. This is the "T" in [ELT](https://en.wikipedia.org/wiki/Extract,_load,_transform). A simple example would be calculating the total amount each customer has spent across all their orders, combining data from two separate source tables into a single clean output.

Meltano uses [dbt](https://www.getdbt.com/) as its transformation tool. dbt operates on the concept of transforms-as-code, where each transform is defined as a templated SQL file committed to your workspace repository. This means transforms are version-controlled, reviewable, and testable in exactly the same way as your pipeline configuration.

All transform files live under the `transforms/models` directory of your workspace repository.

### Step 1 — Create a source

A dbt source defines the raw database schema that your models will read from. Sources are declared in a YAML file, which tells dbt where to find your tables and which schema to use at runtime.

Create a file such as `my_source.yml` under `transforms/models`:

```yaml
version: 2

sources:
  - name: my_source
    schema: "{{ env_var('DBT_SOURCE_SCHEMA') }}"
    tables:
      - name: customers
      - name: orders
```

The `env_var` function pulls the schema name from an environment variable at runtime, so you can point the same model at different schemas across your dev, staging, and prod environments without changing the file.

For the full list of source properties, see the [dbt source properties reference](https://docs.getdbt.com/reference/source-properties).

### Step 2 — Create a model

A dbt model defines a database table that dbt creates and keeps up to date. Each model is a single SQL file that selects and transforms data from your sources.

Create a file such as `my_model.sql` under `transforms/models`:

```sql
{{ config(materialized='table') }}

with customers as (
    select * from {{ source('my_source', 'customers') }}
),
orders as (
    select * from {{ source('my_source', 'orders') }}
),
final as (
  select
    c.id,
    c.name,
    SUM(o.product_price * o.quantity) as total_spend
  from customers c
  join orders o on o.customer_id = c.id
  group by c.id, c.name
  order by total_spend desc
)
select * from final
```

The `{{ config(materialized='table') }}` block at the top tells dbt to create a physical table in your data store each time the model runs. The `{{ source(...) }}` references connect the model to the source tables defined in the previous step.

For a full reference of dbt Jinja functions available in models, see the [dbt Jinja functions docs](https://docs.getdbt.com/reference/dbt-jinja-functions).

### Step 3 — Run your models

dbt models require the source tables to exist before they can run. If the raw data is not yet in your data store, you will need to run your data import locally first (see "Running your data import locally" above).

Once the source data is in place, install and run dbt from your workspace directory:

```bash
# Install the dbt transformer plugin
meltano install transformer dbt

# Run all dbt models in the project
meltano invoke dbt run
```

For the full set of `dbt run` options, see the [dbt run reference](https://docs.getdbt.com/reference/commands/run).

Running transforms in a pipeline: when a pipeline that includes dbt is run in the Meltano platform, all models in the project are executed automatically as part of that pipeline run. You do not need to trigger dbt separately.

---

## Automate actions

This covers going beyond basic data imports to automate more complex workflows: building custom pipelines with full control over plugin execution order, running Jupyter Notebooks on a schedule, and setting up pipeline monitoring so you are notified the moment something goes wrong.

### Create a custom pipeline

**Time required: 5 minutes**

Prerequisites: a Meltano account, a workspace created through the Meltano app or API.

A custom pipeline gives you complete control over which plugins run, in what order, and on what schedule. Unlike a standard data import pipeline, which is tied to a single data source, a custom pipeline lets you chain any combination of installed plugins together. Teams use custom pipelines to run reports, send email notifications, execute tests, or orchestrate multi-step workflows that do not fit the standard extract-load-transform pattern.

Steps:

1. In your workspace, go to **Lab**, then the **Pipelines** page.
2. Click the **+ Pipeline** button in the top right.
3. Fill in the **Name** field, then click the empty square with the plus sign to start adding plugins.
4. In the plugin picker, find the plugin you want to add from either the **Existing** or **New** tabs.

Installing plugins first: you can only add plugins that have already been installed in your workspace. If the plugin you need is not listed, install it first via **Lab** > **Plugins** > **Available**.

5. Repeat step 4 to add as many plugins as your pipeline requires, in the order they should execute.
6. Expand the **Settings** menu, then each plugin's sub-section, and fill in all required fields marked with an asterisk (`*`).
7. In the **Clean, transform and organise** section, choose whether to use the default actions or supply your own custom actions or script.
8. In the **Automate your import** section, choose how often the pipeline should run. Select from the preset schedules or use **Custom** to define your own using cron syntax.
9. Click **Save**. A confirmation bar will appear at the top of the screen.
10. Go back to the **Pipelines** screen. A config job will run for the next one to two minutes to commit your pipeline configuration to your workspace repository.
11. Once the config job has completed, you can run the pipeline manually or let it run on its schedule.

Note: Do not attempt to run the pipeline while the config job is still in progress.

#### Import pipelines

When your custom pipeline includes a data source plugin (an extractor), you can create it as an **import pipeline** instead. Import pipelines automatically include Meltano-supported companion plugins for that data source, such as pre-built data models and datasets that appear in your workspace.

### Execute a Jupyter Notebook on a schedule

**Time required: 10 minutes**

Prerequisites: a Meltano account, a workspace created through the Meltano app or API, a Jupyter Notebook you want to run on a schedule.

Meltano can execute Jupyter Notebooks as part of a pipeline, on whatever schedule you define. This is useful for automating recurring reports, data processing tasks, or machine learning model runs that live in a notebook rather than a standalone script. Once a notebook has run, you can extend the pipeline further to send the output by email, publish it to your workspace, or chain it with other notebooks.

#### Setting up the notebook

1. In your workspace, go to **Lab**, then **Settings** and copy the repository URL.
2. Clone your workspace repository to your local machine:

```bash
git clone https://github.com/YourOrg/your-workspace
```

3. Place your Jupyter Notebook inside the `notebook/` directory of the cloned repository.
4. Commit and push the notebook back to GitHub:

```bash
git add notebook/your_notebook.ipynb
git commit -m "Add scheduled notebook"
git push
```

#### Creating the pipeline

1. In your workspace, go to **Lab**, then **Plugins**.
2. On the **Available** tab, find the **Notebook** plugin and click **Install**.
3. Go to the **Pipelines** page and click **+ Pipeline**.
4. Fill in the **Name** field, then click the square with the `+` sign and add the Notebook plugin from the **New** tab.
5. Expand **Settings** and then the **notebook** sub-section.
6. Fill in the **Path** field with the path to your notebook, for example: `notebook/your_notebook.ipynb`.
7. Expand **Actions**, click **Custom**, and select the appropriate `notebook:` command from the dropdown. Use `notebook:run` as your default unless you need a specific conversion or export behaviour.
8. Expand **Schedule** and choose how often the pipeline should run.
9. Click **Save**. A confirmation bar will appear at the top of the screen.
10. Return to the **Pipelines** screen and wait for the config job to complete (typically 10 to 20 seconds).
11. Once the config job has finished, run the pipeline manually or leave it to its schedule.

#### What to expect when the pipeline runs

When running in Meltano Cloud, no cell outputs or files are committed to the workspace repository after execution. Effects are only visible externally if the notebook triggers an action such as sending an email or a Slack notification.

#### Extending the pipeline

Once the notebook is running on a schedule, you can build on it by chaining additional plugins in the same pipeline.

**Send an email** — Install the Sendgrid plugin from the Plugins page and add it after the Notebook plugin in your pipeline. Configure the recipient, subject, body, and any attachments. You can use the Notebook plugin's built-in PDF conversion to generate a formatted report and attach it automatically.

**Publish the notebook to your workspace** — Install the Meltano plugin from the Plugins page and add it to the pipeline. Configure it to publish the executed notebook to your workspace so other workspace members can view the latest results whenever they need.

**Chain multiple notebooks** — You can add multiple Notebook plugin steps to a single pipeline, passing data or state from one notebook to the next. Each step runs in sequence, in the order defined in the pipeline.

### Watch pipelines

**Time required: 5 minutes**

Prerequisites: a Meltano account, a workspace with at least one pipeline already created.

When pipelines run on a schedule or are triggered automatically, you need to know immediately if something goes wrong. Watching a pipeline subscribes you to notifications for that pipeline, delivered both in the Meltano app and by email. You can choose to be notified only on errors or for all activity.

#### Watching a pipeline

1. In the Meltano app, go to your workspace **Lab** and select **Pipelines**.
2. Find the pipeline you want to monitor and click the eye icon on its row.
3. Select your notification level:

| Option | When you are notified |
|---|---|
| **Errors** | Jobs that ended with an error; jobs that were skipped |
| **All activity** | Jobs that started; jobs that ended (regardless of status) |

Which level to choose: use **Errors** for production pipelines where you only need to act when something breaks. Use **All activity** when you are setting up a new pipeline and want full visibility into its run behaviour until you are confident it is stable.

You can update or remove a watch at any time by clicking the eye icon again on the same pipeline.
