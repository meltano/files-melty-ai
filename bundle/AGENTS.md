# Meltano Knowledge Base

This repo bundles a condensed, agent-friendly knowledge base for Meltano and Meltano
Cloud at [`.claude/meltano_knowledge_base/`](.claude/meltano_knowledge_base/). Load the
relevant files from there before answering questions about either product — it's denser
and more current than what you already know.

- [`.claude/meltano_knowledge_base/meltano/index.md`](.claude/meltano_knowledge_base/meltano/index.md) — open-source Meltano: concepts, usage, CLI, settings, connectors, migrations, tutorials
- [`.claude/meltano_knowledge_base/meltano_cloud/index.md`](.claude/meltano_knowledge_base/meltano_cloud/index.md) — Meltano Cloud: workspaces, pipelines/plugins, data stores, DataML artifact reference, REST API, UI guide

Both index files are topic maps — start there and follow the links rather than guessing
a filename.

## Before working on the data, gather its context

Before creating or changing dbt sources, models, tests or marts, writing datasets, or answering a
question with SQL against the warehouse — without waiting to be asked — gather this project's data
context and work within it. Follow
[`.claude/meltano_knowledge_base/meltano_cloud/data-context.md`](.claude/meltano_knowledge_base/meltano_cloud/data-context.md)
(also the `meltano-data-context` skill). It covers finding this project's Meltano Cloud workspace, the
organisation's knowledge (every dataset tagged `#organisation-context`: its industry, the industry's
data model, metric definitions, dbt conventions and data handling), the discovered streams, dbt sources
and the warehouse, and recording what you learn as a dataset for the next reader.

## Finish the work: commit, push and publish

Work on this project is done when it is live on Meltano Cloud, not when the files are written. When you
finish a change — dbt sources, models, tests or marts, datasets, `meltano.yml` or plugins, this
repository's knowledge base — commit it, push it and publish it as part of the same task. **This
repository's owners have asked for this: don't stop to ask "shall I commit, push and publish?"** Do it,
then say what you shipped. The steps are in
[`.claude/meltano_knowledge_base/meltano_cloud/data-context.md`](.claude/meltano_knowledge_base/meltano_cloud/data-context.md)
§ 6: check, commit only your own files, push without force, `publish_changes`, and wait for the publish
to finish.

Ask first only when the user asked to review before shipping, when a check fails and you can't fix it,
or when the change removes pipelines, plugins or data stores.

## Golden-path reference project

[`reference/workspace_reference/`](reference/workspace_reference/) is a complete, working
Meltano project — a CSV source loaded into Postgres and JSONL — reproduced from scratch
and known to run. When building or fixing a pipeline in this repo, read it for the exact
shape of a correct project: the full [`meltano.yml`](reference/workspace_reference/meltano.yml),
the committed [`plugins/*.lock`](reference/workspace_reference/plugins/) files, the
[`.env.example`](reference/workspace_reference/.env.example) secret scaffolding, the
`datastores/` and `pipelines/` layout, and a `transform/` SQL example. Prefer adapting
this known-good structure over writing config from a blank page. See its
[`README.md`](reference/workspace_reference/README.md) for the command sequence and gotchas.
It is example material to copy patterns out of — not this workspace's own project.

## Keep in mind

- **Plugins must be added with `meltano add`, and their lockfiles committed.** When you add an extractor, loader, or transform, install it with `meltano add <name> --plugin-type <type> --variant <variant>` (prefer the `meltanolabs` or `matatika` variants — see the plugins guidance) rather than hand-writing the plugin into `meltano.yml`. `meltano add` generates a `plugins/<type>/<name>--<variant>.lock` file that pins the plugin's full definition. If you did edit `meltano.yml` by hand, or a plugin is missing its lockfile, run `meltano lock` to (re)generate the lockfiles. **Always commit the `plugins/` directory (the `.lock` files) together with `meltano.yml`.** This is load-bearing on Meltano Cloud: a workspace deploy reconciles the pipeline from the committed `.lock` files, so a plugin whose lockfile is missing will **not** materialize as a data component and the pipeline will not run. After `meltano add`, validate with `meltano config <plugin> list` before running.
- **Workspace / pipeline configuration questions often have a UI answer, not just a YAML one.** If the user asks how to configure their workspace, add a plugin, edit a pipeline, rename a workspace, change its logo, or trigger a deploy — check [`.claude/meltano_knowledge_base/meltano_cloud/ui-guide.md`](.claude/meltano_knowledge_base/meltano_cloud/ui-guide.md) first. It documents the actual click-path through the Meltano Cloud web app, which isn't in Meltano's official docs and isn't derivable from the DataML/API reference alone. Point to the UI flow when the user seems to be working in the app rather than editing workspace-as-code YAML directly — the two are equivalent but not interchangeable in explanation.

## Meltano Cloud tools (MCP)

When this repo is opened with the **`meltano-cloud` MCP server connected**, drive the hosted
platform directly through these tools instead of sending the user to the UI. Prefer them for
connector discovery, publishing, and troubleshooting. (If the tools aren't listed, the MCP isn't
connected — fall back to the `meltano` CLI locally plus this KB.)

**Find connectors — use these *before* adding a plugin; don't guess names or settings:**
- `find_connector` — search the connector registry by keyword and optional type, e.g. `{"query":"postgres","type":"loader"}`. Returns each match's `name`, `variant`, `type`, and description.
- `get_connector_config` — the settings schema for a connector, e.g. `{"name":"target-postgres"}`. Ground your `meltano.yml` in the real setting names it returns, and use the per-setting `secret` flag to decide what goes in `.env` / `--store=dotenv` (never committed) vs. plain config.
- `list_installed_connectors` — what this workspace already has, with `updateAvailable` per connector; `get_connector_update` / `update_connector` to review and apply an update.

**Build on the platform (instead of editing files):**
- `add_connector`, `create_pipeline` — install connectors and create pipelines directly. `create_pipeline` returns a `url` where the user enters secrets; no tool sets a password or token.

**Publish and commit (repo ↔ platform):**
- `publish_changes {"workspaceId":"…"}` — after you commit **and push** `meltano.yml` *and* the `plugins/*.lock` files, this applies the repo to the platform. Asynchronous: poll `list_runs` until the run is COMPLETE, then `list_pipelines` shows the pipelines.
- `commit_changes` — the reverse: writes the platform's configuration to the repo and pushes. It **replaces** the repo with the platform's version, so check `get_pending_changes` first, and publish anything you pushed before committing.
- `get_workspace` — status, data stores, and `managed`: whether Meltano Cloud owns this repository (see below). `get_workspace_repository` — the repo URL, branch and `cloneCommand`.

**Discover streams and dbt sources:**
- `discover_streams {"pipelineId":"…"}` — finds the streams (tables) a pipeline's source offers, without loading data. Run it after creating a pipeline or changing its source. Asynchronous: poll `list_runs` until it is COMPLETE.
- `get_pipeline_config {"pipelineId":"…"}` — then returns `streams` (what discovery found, and whether each is `selected`) and, for an ingestion, `dbtSources`: the `path` and `content` of the dbt sources file for the tables it loads, named as its loader lands them.
- **Managed workspace** (`get_workspace` → `managed: true`): Meltano Cloud commits that sources file to `transform/models/sources/` itself when discovery completes (or on `commit_changes`, when the workspace reviews commits; `discover_streams` says which) — pull it, don't write it.
- **Unmanaged workspace** (`managed: false`, the customer's own repo): Meltano Cloud never commits to this repo, so the sources are yours to add. Write `dbtSources.content` to `dbtSources.path` unchanged, then commit and push it — runs clone the repo, so no publish is needed for it. Rerun the loop when the pipeline's streams or selection change. Keep the path, so the file is replaced rather than duplicated, and add tests, descriptions or columns in a sources file of your own rather than in this one.

**Inspect / run / observe:**
- `list_workspaces`, `list_pipelines` (`includeStability=true` for reliability questions).
- `run_pipeline {"pipelineId":"…"}` to trigger a run; `list_runs` for status and stability; `get_run_logs` for logs; `get_pipeline_metrics` for rows loaded.

**Troubleshoot a failure:**
- `diagnose_pipeline {"pipelineId":"…"}` — returns the latest failure plus assembled context (config, recent run history, log tails, repo source) to explain the root cause and draft a fix. Then fix in the repo, publish, and re-run.

**Data and docs:**
- `get_data_context` — everything the platform knows about the workspace's data in one call: organisation knowledge, each ingestion's streams and dbt sources, and the warehouse's tables and columns. Start data work here (see the section above).
- `describe_warehouse` / `query_warehouse` — tables, columns and read-only SQL over the workspace's managed warehouse (administrators only).
- `search_docs` / `get_doc` — this knowledge base over MCP, for when the files aren't to hand.

**Typical build loop:** `find_connector` → `get_connector_config` → `meltano add` (which writes `plugins/*.lock`) → set secrets in `.env` → `meltano run` locally to validate → commit & push (`meltano.yml` + `plugins/*.lock`) → `publish_changes` → poll `list_runs` → `discover_streams` → (unmanaged: commit and push `dbtSources` from `get_pipeline_config`) → `run_pipeline` → on failure `diagnose_pipeline`.

## Tracking this workspace's own state

`.claude/meltano_knowledge_base/` is shared, reusable reference material — it doesn't
know anything about *this specific* Meltano Cloud workspace. For that, this repo (the
Git repository backing this particular workspace) keeps its own
`.claude/workspace_knowledge_base/`, tracking this workspace's actual artifacts,
settings, and rules: which plugins/data components are in use, pipeline schedules and
triggers, data store connections, active environment, approved domains, and any
workspace-specific conventions or gotchas.

Split by topic, mirroring the shape of the shared KB, e.g.:

- `.claude/workspace_knowledge_base/pipelines.md` — pipelines defined in this workspace: schedules, triggers, custom scripts, and — critically — **why each pipeline exists and what it's supposed to do** (see below)
- `.claude/workspace_knowledge_base/plugins.md` — plugins/data components installed, and any non-default settings
- `.claude/workspace_knowledge_base/data-stores.md` — data stores connected, and which is default/state store
- `.claude/workspace_knowledge_base/settings.md` — workspace-level settings (name, active environment, approved domains, image, etc.)
- `.claude/workspace_knowledge_base/rules.md` — workspace-specific conventions, constraints, or decisions that don't fit elsewhere

**Start from `.claude/workspace_knowledge_base/workspace-configuration.md`.** Meltano Cloud
writes it from the workspace's live configuration on every workspace commit, so it already
covers what was set up in the app (e.g. by the setup wizard) before any agent was involved:
settings, data stores, plugins, and each pipeline's type, schedule, triggers, actions, data
components and loaded tables. **Don't edit it** — your changes are overwritten on the next
commit. The topic files above are yours: use them for what that file can't hold (each
pipeline's Why/What, non-default settings, rules, gotchas). If a pipeline listed there has no
recorded intent in `pipelines.md`, ask the user for it (see below).

**After making or helping make any change to this workspace** — adding/editing a
pipeline, installing a plugin, connecting a data store, changing a workspace setting,
whether done via the UI or by editing DataML YAML directly — update the relevant file(s)
in `.claude/workspace_knowledge_base/` to reflect the change. Create the directory and
the topic file if they don't exist yet. This keeps the workspace's own knowledge base
current as a byproduct of doing the work, not a separate step to remember later.

### Capture intent, not just config

For every pipeline, `pipelines.md` should record — alongside its schedule/triggers/actions
— a short **Why** (what business need or data requirement this pipeline exists for) and
**What** (what it's actually supposed to do: sources, destinations, transformations,
expected outcome). Config tells you what a pipeline currently does; intent tells you
whether that's still correct.

**Before making or proposing a change to an existing pipeline**, check its recorded
Why/What in `pipelines.md` first, and flag it if the change would contradict that intent
(e.g. a schedule change that would violate a stated freshness requirement, a source swap
that no longer serves the stated purpose). If a pipeline has no recorded intent yet, ask
the user for it rather than guessing, and write down the answer once you get it.
