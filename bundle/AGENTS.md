# Meltano Knowledge Base

This repo bundles a condensed, agent-friendly knowledge base for Meltano and Meltano
Cloud at [`.claude/meltano_knowledge_base/`](.claude/meltano_knowledge_base/). Load the
relevant files from there before answering questions about either product — it's denser
and more current than what you already know.

- [`.claude/meltano_knowledge_base/meltano/index.md`](.claude/meltano_knowledge_base/meltano/index.md) — open-source Meltano: concepts, usage, CLI, settings, connectors, migrations, tutorials
- [`.claude/meltano_knowledge_base/meltano_cloud/index.md`](.claude/meltano_knowledge_base/meltano_cloud/index.md) — Meltano Cloud: workspaces, pipelines/plugins, data stores, DataML artifact reference, REST API, UI guide

Both index files are topic maps — start there and follow the links rather than guessing
a filename.

## Keep in mind

- **Workspace / pipeline configuration questions often have a UI answer, not just a YAML one.** If the user asks how to configure their workspace, add a plugin, edit a pipeline, rename a workspace, change its logo, or trigger a deploy — check [`.claude/meltano_knowledge_base/meltano_cloud/ui-guide.md`](.claude/meltano_knowledge_base/meltano_cloud/ui-guide.md) first. It documents the actual click-path through the Meltano Cloud web app, which isn't in Meltano's official docs and isn't derivable from the DataML/API reference alone. Point to the UI flow when the user seems to be working in the app rather than editing workspace-as-code YAML directly — the two are equivalent but not interchangeable in explanation.

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
