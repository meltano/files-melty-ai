# Data Context

What to read before working on a Meltano project's data, and where each piece comes from. "Working on
the data" means creating or changing dbt sources, models, tests or marts, writing datasets, or
answering a question with SQL against the warehouse. Read the context first: work done without it
guesses at names, types, definitions and conventions the project already has.

This applies to every Meltano project, whether or not Meltano Cloud manages its repository.

## 1. Find the workspace

Skip this when the project isn't on Meltano Cloud. Without the workspace, only the repository's
sources below are available.

- A repository Meltano Cloud manages names its workspace in
  `.claude/workspace_knowledge_base/workspace-configuration.md`, under **Workspace ID**.
- Otherwise, with the Meltano Cloud MCP tools connected, call `list_workspaces`. The workspace is the
  one whose `repositoryUrl` matches this repository's git remote (`git remote get-url origin`), ignoring
  a `.git` suffix and `https://` versus `git@` forms. Ask the user only when none or several match.

## 2. Gather the context

| Source | What it holds | In the repository | Over MCP |
|---|---|---|---|
| Organisation knowledge | The organisation's industry; its industry's context (data model, metric definitions, dbt modelling conventions, data handling); anything its people have recorded | Every dataset tagged `#organisation-context`: `grep -rl '#organisation-context' analyze/datasets` | `get_data_context` → `organisationKnowledge` |
| Workspace configuration | Settings, data stores, plugins, each pipeline's type, schedule and loaded tables | `.claude/workspace_knowledge_base/workspace-configuration.md`, and the other files of that directory (pipeline intent, rules) | `get_workspace`, `list_pipelines` |
| Discovered streams | Every stream each ingestion's source offers, and whether it is selected | — | `get_data_context` → `ingestions[].streams` |
| dbt sources | The tables each ingestion loads, named as its loader lands them | `transform/models/sources/*.yml` (generated files are marked `meta: meltano-cloud`) | `get_data_context` → `ingestions[].dbtSources` |
| The warehouse | Tables and columns with their real types, row estimates, the pipeline that loads each table, comments dbt persisted | — | `get_data_context` → `warehouse` (administrators only); `query_warehouse` for anything else |
| Existing datasets and models | What has already been built and how it is described | `analyze/datasets/`, `transform/models/` | `describe_warehouse` → `datasets` |

With the MCP tools connected, `get_data_context` returns most of this in one call. Its `notes` say what
it left out (for example the warehouse, for someone who isn't an administrator), and its `message` says
how to use the rest.

## 3. Profile what the context doesn't say

Before modelling a table the context says little about, measure it. With `query_warehouse` (read-only,
one statement at a time):

- row count, and for each column: null fraction, distinct count, min and max;
- `pg_stats` holds Postgres's own statistics (`null_frac`, `n_distinct`) for analysed tables at no
  scanning cost; `pg_total_relation_size('schema.table')` gives a table's size;
- whether a text column holds numbers, dates or JSON, which decides its type in staging.

Record statistics, not values. Never copy names, email addresses, account numbers or other personal
data out of the warehouse into files, datasets or answers.

## 4. Work within it

- Follow the organisation knowledge: its metric definitions, modelling conventions and data-handling
  rules. Say so when a request conflicts with them rather than silently choosing one.
- Take table names, column names and types from the warehouse or the discovered streams, never from
  memory.
- Add columns, descriptions and tests in a sources file of your own beside the generated one, never
  in a generated file (it is rewritten).

## 5. Record what you learned

Write what you found out about the data, so the next person or agent starts from it rather than
profiling again: a dataset with no query, tagged `#organisation-context`, for example
`analyze/datasets/context/<source>.yml`:

```yaml
version: datasets/v0.3
title: "Google Sheets: what the raw data holds"
description: |
  - `analytics.demo_financial_data`: 1,204 rows. `amount` is text holding decimals with a comma
    thousands separator; `posted` is a dd/mm/yyyy date; `notes` is empty in 97% of rows.
  - Personal data: `customer_email`. Mask it outside staging.

  #organisation-context
```

Keep it to what isn't obvious from the column names and types: meanings, units, formats, gaps and
caveats. Commit it with the work. In a repository Meltano Cloud doesn't manage, call `publish_changes`
after pushing so the platform loads it.
