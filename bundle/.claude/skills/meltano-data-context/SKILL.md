---
name: meltano-data-context
description: Gather a Meltano project's data context - the organisation's knowledge, discovered streams, dbt sources and the warehouse's real tables and columns - before creating or changing dbt sources, models, tests or marts, writing datasets, or answering questions with SQL against the warehouse. Use it whenever work touches the project's data, without waiting to be asked.
---

# Meltano data context

Read [`.claude/meltano_knowledge_base/meltano_cloud/data-context.md`](../../meltano_knowledge_base/meltano_cloud/data-context.md)
and follow it. It is kept up to date with the platform; this file is not.

In short:

1. **Find the workspace**: from `.claude/workspace_knowledge_base/workspace-configuration.md`, or by
   matching this repository's git remote to a workspace's `repositoryUrl` over MCP.
2. **Gather the context**: the datasets tagged `#organisation-context`, the workspace configuration, the
   discovered streams, the dbt sources and the warehouse (one call over MCP: `get_data_context`).
3. **Profile what it doesn't say**: statistics only, never personal data.
4. **Work within it**: the organisation's definitions and conventions; real names and types.
5. **Record what you learned**: a dataset tagged `#organisation-context`, shipped with the work.
6. **Ship it without asking**: check, commit your own files, push, `publish_changes`, wait for the
   publish, run what builds the new models, then show the user their results.
