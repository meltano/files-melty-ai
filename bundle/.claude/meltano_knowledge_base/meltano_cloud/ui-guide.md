# Meltano Cloud UI Guide

Practical navigation notes for getting things done in the Meltano Cloud web app — editing
pipelines, adding plugins, and managing workspace settings through the UI. This is *not*
derived from the official docs (they don't cover UI navigation) — it's first-hand
operational knowledge, kept here so it lives alongside the DataML/API reference in
[`index.md`](index.md). Where the UI and the workspace-as-code YAML files
([`dataml-pipelineml.md`](dataml-pipelineml.md), [`dataml-workspaceml.md`](dataml-workspaceml.md))
overlap, both routes are noted.

> Screens and flows can change as the product evolves — if something here looks stale,
> trust what's on screen and update this file.

## Editing a pipeline

1. Go to your **Workspace** — this lands you on the **Pipelines** screen.
2. Scroll to find the pipeline you want, click the **⋮** (three dots) menu next to it, and choose **Edit**.
3. The edit screen has four tabs, each replacing the whole screen when selected:

### Settings

Lists every plugin attached to the pipeline. Click the arrow next to a plugin to expand it
and see its settings.

- Required settings are marked with `*`.
- If you try to save without filling in all required (`*`) settings, the UI blocks the save and shows an error listing what's missing.
- This is the UI equivalent of the `properties` map in a pipeline's YAML file (see [PipelineML → Key Fields](dataml-pipelineml.md)) — settings changed here are the same values you'd otherwise set as `<plugin-name>.<setting>: value` in `pipelines/*.yml`.
- **Some plugins offer OAuth as an alternative to filling in the `*` fields by hand.** When a plugin supports it, the expanded settings panel shows a **Sign in with...** (or similar) button alongside the manual fields. Clicking it runs an OAuth consent flow and populates the relevant auth settings (tokens, etc.) automatically instead of you sourcing and pasting them in yourself. Not every plugin supports this — it depends on whether the connector has an OAuth flow defined. When it's not offered, filling in the required (`*`) fields manually is the only path.

### Streams

Not covered yet.

### Actions

Defines what the pipeline actually runs. Either:
- **Meltano-defined commands** — pick from predefined actions (equivalent to the `actions` list in the pipeline YAML), or
- **A custom script** — free-form Bash, where you write out whatever CLI commands the pipeline should run (equivalent to `inline_script` — see [PipelineML → Custom Scripts](dataml-pipelineml.md)).

This tab also holds **Timeout** and **Max Retries** (equivalent to the `timeout` and `max_retries` YAML fields).

### Triggers

Configures:
- The pipeline's **schedule** (equivalent to the `schedule` cron field), and
- Which other pipelines, if any, trigger this pipeline on their successful completion (equivalent to `triggered_by`).

## Adding a plugin

Plugins are added at the **workspace level**, not from inside a pipeline's edit screen.

1. Go to **Workspace → Plugins**.
2. There are three tabs: **INSTALLED**, **AVAILABLE**, **CUSTOM**.
3. Click **AVAILABLE**, find the plugin you want, and click **Install**.

What happens next depends on how the workspace is backed:

- **Meltano Cloud–managed repo (the common case, not a private/BYO repo):** clicking Install kicks off a **workspace management job**. This job adds the plugin to the workspace via the API, then commits and pushes the resulting config change to the workspace's backing GitHub repository automatically — you don't need to touch Git yourself.
- Once installed, the plugin becomes available to reference from pipelines (add it as a `data_component` / attach it in a pipeline's Settings tab, per the flow above).

This is the UI equivalent of adding a plugin to `meltano.yml` and referencing it in a pipeline's `data_components` — see [Pipelines and Plugins](pipelines-and-plugins.md) for the code-first version of this workflow.

## Workspace settings — general actions

Workspace-level settings (name, approved domains, logo, active environment, repository
connection fields, deployment secret) live on a single **Workspace → Settings** screen —
see [Workspaces → Workspace settings reference](workspaces.md#workspace-settings-reference)
for the full field list, since those fields are already documented there.

Three buttons apply to the whole settings screen:

- **Save** — persists your changes to the workspace's settings.
- **Deploy** — triggers a deployment of the workspace (same effect as a push-triggered deploy, or the `triggered_by: deploy` hook in PipelineML — see [PipelineML](dataml-pipelineml.md)).
- **Delete** — deletes the workspace. Destructive — see [Workspaces → Delete Workspace](workspaces.md) before using it.

### Renaming a workspace

Edit **Name** on the Settings screen and **Save**. Renaming also renames the associated
repository — this can break existing automation that references the old name (see
[Workspaces → General](workspaces.md#general)).

### Changing the logo

Upload a new image under **Image** on the Settings screen and **Save**.
