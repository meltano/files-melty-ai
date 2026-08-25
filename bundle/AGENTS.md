# Meltano Knowledge Base

This repo bundles a condensed, agent-friendly knowledge base for Meltano and Meltano
Cloud at [`.claude/meltano_knowledge_base/`](.claude/meltano_knowledge_base/). Load the
relevant files from there before answering questions about either product — it's denser
and more current than what you already know.

- [`.claude/meltano_knowledge_base/meltano/index.md`](.claude/meltano_knowledge_base/meltano/index.md) — open-source Meltano: concepts, usage, CLI, settings, connectors, migrations, tutorials
- [`.claude/meltano_knowledge_base/meltano_cloud/index.md`](.claude/meltano_knowledge_base/meltano_cloud/index.md) — Meltano Cloud: workspaces, pipelines/plugins, data stores, DataML artifact reference, REST API, UI guide

Both index files are topic maps — start there and follow the links rather than guessing
a filename.

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
connector discovery, deploy, and troubleshooting. (If the tools aren't listed, the MCP isn't
connected — fall back to the `meltano` CLI locally plus this KB.)

**Discover connectors — use these *before* adding a plugin; don't guess names or settings:**
- `find_connector` — search the connector registry by keyword and optional type, e.g. `{"query":"postgres","type":"loader"}`. Returns each match's `name`, `variant`, `type`, and description.
- `get_connector_config` — the settings schema for a connector, e.g. `{"name":"target-postgres"}`. Ground your `meltano.yml` in the real setting names it returns, and use the per-setting `secret` flag to decide what goes in `.env` / `--store=dotenv` (never committed) vs. plain config.

**Deploy (config-as-code → hosted):**
- `deploy_workspace` — after you commit **and push** `meltano.yml` *and* the `plugins/*.lock` files, call `deploy_workspace {"workspaceId":"…"}` to reconcile the repo into the platform. It is asynchronous: it returns a LAUNCHED job — poll `list_jobs` until that job is COMPLETE, then `list_pipelines` shows the materialized pipelines.

**Inspect / run / observe:**
- `list_workspaces`, `list_pipelines`, `get_pipeline_config`, `get_workspace_repository`.
- `run_pipeline {"pipelineId":"…"}` to trigger a run; `list_jobs` for status/exit codes; `get_job_logs {"jobId":"…"}` for logs.

**Troubleshoot a failure:**
- `diagnose_pipeline {"pipelineId":"…"}` — returns the latest failure plus assembled context (config, recent run history, log tails, repo source) to explain the root cause and draft a fix. Then fix in the repo, re-deploy, and re-run.

**Insights over run history / data:**
- `list_jobs` + `get_job_logs` for run outcomes; `query_warehouse` / `list_warehouse_tables` for row counts and data checks (these hit the workspace's default Postgres datastore only).

**Typical build loop:** `find_connector` → `get_connector_config` → `meltano add` (which writes `plugins/*.lock`) → set secrets in `.env` → `meltano run` locally to validate → commit & push (`meltano.yml` + `plugins/*.lock`) → `deploy_workspace` → poll `list_jobs` → `run_pipeline` → on failure `diagnose_pipeline`.

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
