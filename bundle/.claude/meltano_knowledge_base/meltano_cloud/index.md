# Meltano Cloud Knowledge Base

Condensed, plain-Markdown reference for Meltano Cloud (Matatika's managed data platform
built on Meltano), derived from the Docusaurus docs in `docs/docs/meltano-cloud/` and
`docs/docs/reference/cloud/`, plus first-hand UI operational knowledge not covered in the
official docs. Written for use as context for AI coding agents (Claude/Codex) and for
humans — no Docusaurus/MDX syntax, frontmatter, or JSX remains; all YAML, commands, and
API examples are preserved verbatim from source.

For open-source Meltano itself (the underlying ELT framework), see
[`../meltano/index.md`](../meltano/index.md).

## Start here

- [Overview](overview.md) — what Meltano Cloud is and how it relates to open-source Meltano
- [Workspaces](workspaces.md) — creating/managing a workspace, environments, DataOps promotion, members

## Building pipelines

- [Pipelines and Plugins](pipelines-and-plugins.md) — adding plugins, choosing a plugin variant (prefer `meltanolabs`), importing data, transforming with dbt, automating actions and custom scripts
- [Data Stores](data-stores.md) — connecting Snowflake, Microsoft SQL Server, ClickHouse, MotherDuck
- [Operations](operations.md) — pipeline diagnosis, log routing/monitoring, profile & security, local dev setup
- [UI Guide](ui-guide.md) — hands-on UI navigation: editing a pipeline's settings/actions/triggers, installing plugins via the Plugins page, and the workspace Settings screen's Save/Deploy/Delete actions (not covered in the official docs)

## DataML artifact reference (workspace-as-code YAML)

The YAML files that define a Meltano Cloud workspace declaratively:

- [WorkspaceML](dataml-workspaceml.md) — `workspace.yml`: workspace config, dashboards, invitations
- [PipelineML](dataml-pipelineml.md) — `pipelines/*.yml`: schedule, actions, custom scripts, environment
- [DatastoreML](dataml-datastoreml.md) — `datastores/*.yml`: data warehouse destinations
- [ChannelML](dataml-channelml.md) — `analyze/channels/*.yml`: grouping datasets
- [DatasetML](dataml-datasetml.md) — `analyze/datasets/*.yml`: charts/insights, metadata, query, visualisation, worked examples

## REST API reference

- [API Overview](api-overview.md) — auth, error format, HAL link/pagination conventions, resource index
- [API Resources](api-resources.md) — endpoints and field reference for every resource (accounts, pipelines, workspaces, datasets, etc.)
