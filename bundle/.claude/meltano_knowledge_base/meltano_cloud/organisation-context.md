# Organisation Context

What the organisation behind a Meltano Cloud workspace is. For now that is its **industry**. Some
industries also have an **industry context bundle**: a file bundle of datasets that brief the people
and AI assistants in the workspace on the industry. Each dataset has no query. Read the bundle's
datasets before building or changing pipelines, dbt models or datasets, so the work fits the
industry.

## Organisation knowledge: `#organisation-context`

Every dataset tagged **`#organisation-context`** is part of the organisation's knowledge: the industry
dataset below, every dataset of an industry context bundle, and any dataset the workspace's own
people tag the same way (put `#organisation-context` in its description).

**Before creating or changing dbt models, pipelines or datasets, and before querying the warehouse,
pull it into context:**

- Over MCP, call `get_organisation_knowledge` with the workspace ID. It returns the full text of every
  tagged dataset, the organisation context first.
- In a clone of the workspace repository, read the files that
  `grep -rl '#organisation-context' analyze/datasets` lists.

Then follow its definitions, conventions and data-handling rules, and say so when a request conflicts
with them.

## Where it lives

The industry is a dataset with the alias `organisation-context`, kept in the workspace repository at:

```
analyze/datasets/organisation-context.yml
```

```yaml
version: datasets/v0.3
title: Organisation context
description: |
  - **Industry:** Financial Services

  Context about the industry is in the datasets of the `files-context-financial-services` file bundle.

  #organisation-context
raw_data: |-
  {
    "industry" : "Financial Services"
  }
```

`raw_data` is the context: it is what Meltano Cloud reads back. The `description` is generated from
it, so edit `raw_data`, not the description.

## Industry context bundles

Each bundle has the same five datasets about its industry: an overview with its segments and source
systems, its data model, key metrics, dbt modelling conventions, and data handling.

| Industry | Bundle | Datasets |
|---|---|---|
| Agriculture | `files-context-agriculture` | `analyze/datasets/agriculture/` |
| Construction | `files-context-construction` | `analyze/datasets/construction/` |
| Education | `files-context-education` | `analyze/datasets/education/` |
| Energy & Utilities | `files-context-energy-utilities` | `analyze/datasets/energy-utilities/` |
| Financial Services | `files-context-financial-services` | `analyze/datasets/financial-services/` |
| Government & Public Sector | `files-context-government-public-sector` | `analyze/datasets/government-public-sector/` |
| Healthcare & Life Sciences | `files-context-healthcare-life-sciences` | `analyze/datasets/healthcare-life-sciences/` |
| Hospitality & Travel | `files-context-hospitality-travel` | `analyze/datasets/hospitality-travel/` |
| Manufacturing | `files-context-manufacturing` | `analyze/datasets/manufacturing/` |
| Media & Entertainment | `files-context-media-entertainment` | `analyze/datasets/media-entertainment/` |
| Non-profit | `files-context-non-profit` | `analyze/datasets/non-profit/` |
| Professional Services | `files-context-professional-services` | `analyze/datasets/professional-services/` |
| Real Estate | `files-context-real-estate` | `analyze/datasets/real-estate/` |
| Retail & E-commerce | `files-context-retail-ecommerce` | `analyze/datasets/retail-ecommerce/` |
| Technology & Software | `files-context-technology-software` | `analyze/datasets/technology-software/` |
| Telecommunications | `files-context-telecommunications` | `analyze/datasets/telecommunications/` |
| Transport & Logistics | `files-context-transport-logistics` | `analyze/datasets/transport-logistics/` |

Other is recorded in the dataset, with no bundle. The MCP tool
`get_organisation_context` returns the industries it takes as `industries`. Prefer it over this
table when they differ.

## How it gets there

| Workspace | How the industry is set | How it reaches the repository |
|---|---|---|
| Repository managed by Meltano Cloud | The setup wizard's Industry step, `create_workspace`, or `set_organisation_context` | Meltano Cloud installs the bundle and commits both the dataset and the bundle's datasets |
| **Created from an existing Meltano project** (your own repository) | `create_workspace` or `set_organisation_context` | **Not automatically.** Meltano Cloud never pushes to a repository it does not manage. Follow the steps below |

## Adding it to your own repository with MCP

For a workspace created from an existing repository, an agent connected to Meltano Cloud, working in
a clone of that repository, can add the context like this:

1. Call `get_organisation_context` with the workspace ID. If it has no industry yet, ask the user
   which industry their organisation is in, and call `set_organisation_context` with it.
2. Write the returned `content` to the returned `path` (normally
   `analyze/datasets/organisation-context.yml`). Do not rename the file: its name is the dataset
   alias, and the platform finds the context by it.
3. If the result has a `bundle`, save `bundle.pluginDefinition` to a file outside the project (for
   example `/tmp/files-context-financial-services.yml`) and run, in the project directory:

   ```sh
   meltano add --plugin-type files files-context-financial-services --from-ref /tmp/files-context-financial-services.yml
   ```

   This adds the bundle to `meltano.yml` and writes its datasets into
   `analyze/datasets/financial-services/`. A plain `meltano install` does not write a bundle's files;
   `meltano add` does.
4. Commit and push to the branch the workspace deploys from.
5. Call `publish_changes` so the platform loads the new datasets.

The result's `message` lists the same steps for the workspace in hand.

To change the industry later, call `set_organisation_context` and repeat steps 2–5. A bundle added for
an earlier industry stays in the project until you remove it.
