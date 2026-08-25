# files-melty-ai
Knowledge base for Meltano &amp; Meltano Cloud — condensed docs + UI notes, built for use as AI agent context (Claude/Codex) and human reference.

## Layout

[`bundle/`](bundle/) is the **seed image** — it mirrors, file-for-file, what a customer
workspace repository receives. It is the single source of truth vendored into the platform
(`matatika-catalog`) and shipped as the pip package:

- [`bundle/AGENTS.md`](bundle/AGENTS.md) — agent router; [`bundle/CLAUDE.md`](bundle/CLAUDE.md) — pointer to it
- [`bundle/.claude/meltano_knowledge_base/`](bundle/.claude/meltano_knowledge_base/) — shared KB for `meltano` and `meltano_cloud`
- [`bundle/reference/workspace_reference/`](bundle/reference/workspace_reference/) — a complete, known-good golden-path Meltano project

Because `bundle/` **is** the seed image, vendoring it downstream is a single recursive copy
(plus the `.claude`→`claude` rename Maven resources require).
