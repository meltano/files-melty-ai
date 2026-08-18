# Meltano Knowledge Base

Condensed, plain-Markdown reference for open-source Meltano (the ELT/data-integration
framework), derived from the Docusaurus docs in `docs/docs/`. Written for use as context
for AI coding agents (Claude/Codex) and for humans — no Docusaurus/MDX syntax, frontmatter,
or JSX remains; all commands, YAML, and code examples are preserved verbatim from source.

For Meltano Cloud (Matatika's managed platform built on Meltano), see
[`../meltano_cloud/index.md`](../meltano_cloud/index.md).

## Start here

- [Overview](overview.md) — what Meltano is, its philosophy, Open vs Cloud
- [Getting Started](getting-started.md) — install Meltano and walk through your first pipeline
- [Concepts](concepts.md) — projects, plugins, environments, state backends, virtual envs

## Day-to-day usage

- [Usage: Plugin Management and Configuration](usage.md) — adding/installing plugins, how configuration is layered and sourced
- [Data Pipelines: Extraction, Loading, and Mapping](data-pipelines.md) — running EL(T), stream/property selection, incremental state, inline mapping
- [Transformation and Orchestration](transformation-and-orchestration.md) — dbt integration, scheduling, Airflow
- [Connectors](connectors.md) — extractor/loader overview plus specific connector setup notes

## Deploying and operating

- [Installation](installation.md) — in-depth install guide (pipx/uv, Docker, per-OS notes)
- [Deployment and Operations](deployment-and-operations.md) — containerization, production config, logging, analysis, advanced topics, custom state backends
- [Troubleshooting and Debugging](troubleshooting-and-debugging.md) — diagnosing pipeline/plugin problems, debugging a custom extractor
- [Migration Guides](migration-guides.md) — v2/v3/v4 breaking changes and dbt project migration

## Reference

- [CLI Reference](cli-reference.md) — every `meltano` command, flags, and examples
- [Settings Reference](settings-reference.md) — all built-in settings, env vars, defaults
- [Plugin Definition Syntax](plugin-definition-syntax.md) — YAML syntax for defining/contributing plugins
- [Glossary](glossary.md) — terminology used across the docs
- [Tutorials](tutorials.md) — building a custom extractor, Jupyter, DataHub, example projects
