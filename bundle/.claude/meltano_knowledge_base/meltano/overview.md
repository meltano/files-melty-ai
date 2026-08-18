# Meltano Overview

What Meltano is, its core philosophy, and how to choose between Meltano Open and Meltano Cloud.

## What Meltano Is

Meltano is a declarative data integration engine for building ELT (Extract, Load, Transform) pipelines. It provides the glue to make extractors, loaders, and transformation/orchestration tools work together smoothly, with consistent configuration and deployment.

It is an Open Source DataOps Infrastructure: you can move data with a strong developer experience while also managing all of the data tools in your stack. You collaboratively build and improve your data platform like a software project — spinning up a service or tool (Singer connectors, Airflow, dbt, Great Expectations, Snowflake, etc.) and configuring, deploying, and managing it through a single control plane.

Developed since 2018, Meltano runs in production at large companies like GitLab and currently powers over a million pipeline runs monthly.

## Core Philosophy

### Code-first / DataOps out-of-the-box

A Meltano project is just a directory of text-based files (`meltano.yml` plus supporting files). This means it can be treated like any other software project: version control, code review, and CI/CD all apply naturally. Meltano provides tooling that makes these DataOps best practices easy to use in every project.

### Plugin-based / modular

Meltano takes a modular approach to data engineering: your project and pipelines are composed of **plugins** of different types — most notably **extractors** (Singer taps), **loaders** (Singer targets), and **utilities** (dbt for transformation, Airflow/Dagster for orchestration, and much more via MeltanoHub). Meltano Hub hosts base plugin descriptions ("discoverable plugins") for hundreds of these components so they work out of the box.

### ELT (Extract, Load, Transform)

Meltano's pipeline model extracts data from a source, loads it into a destination (usually a database or warehouse), and then transforms it in place — as opposed to the older ETL model where transformation happens before loading. The core workflow is:

1. **Extract data** from data sources and load it into targets.
2. **Transform data** inside a database (typically with dbt).
3. **Orchestrate** the extract/load/transform process (typically with Airflow).
4. Optionally add further steps: testing data with dbt tests or Great Expectations, running analyses in Jupyter notebooks, visualizing with Superset, etc.

Meltano lets you do any combination of these steps inside your Meltano project, controlled by the Meltano CLI.

## Why Companies Build With Meltano

- **No lock-in** — open source with a strong community.
- **Extensible from day one** — easy to add a custom connection using the SDK (for Singer taps/targets) or EDK (for Meltano components).
- **Amazing developer experience** — go from start to finish on a new data project (extraction, loading, transforming, orchestrating) within days.
- **Small surface area** — features like inline data mappings make it easy to strip unnecessary information out of pipelines, helping with security/GDPR compliance.

### Key features

- **Start simple** — pip-installable and available as a prepackaged Docker container; a first ELT pipeline can be running within minutes.
- **Integrates with everything** — 300+ natively supported data sources and targets, plus plugins like Great Expectations or dbt.
- **Easily customizable** — the Singer SDK and the Meltano EDK make it straightforward to build new connectors and components. Meltano Hub helps you find connectors and components built across the community.
- **First-class ELT tooling built in** — extract from any source, load into any target, use inline maps to transform data on the fly, and test incoming data, all in one package.

## Which Meltano: Open vs Cloud

Meltano ships as two products:

**Meltano Open** — the core Singer-based ELT engine. Open source (MIT license). Bring your own orchestration, storage, and infrastructure; fully self-managed. This is Meltano Community: install it locally or on your own servers, define pipelines in code, and run them using the CLI or your own orchestrator (Airflow, Dagster, Prefect, or any scheduler you already use). Everything lives in `meltano.yml` — version-controlled and reproducible.

**Meltano Cloud** — a fully managed hosted service. Hosted pipelines, workspaces, secrets, and monitoring, with no infrastructure to run.

### Feature comparison

| Features | Open | Cloud |
|---|---|---|
| Connectors | 600+ connectors | 600+ and custom connectors |
| Pipeline hours | Self managed, not applicable | Unlimited |
| Users | Only you | Unlimited |
| Setup | Well documented, self-setup | Easy, stress-free and managed setup |
| Account management | — | Dedicated |
| Engineer on demand / mo | — | Starting from 8hrs/mo |
| Build with agents | Yes | Yes |
| Reverse ETL connections | Yes | Yes |
| API | — | Yes |
| Workspaces | — | Yes |
| Direct engineer Slack access | — | Yes |
| Enterprise grade security | — | Yes |
| AI Data Engineer Agent | — | Yes |

Choose **Open** if you want full control over infrastructure and are comfortable self-hosting. Choose **Cloud** if you want a managed service with unlimited pipeline hours, users, and dedicated support.
