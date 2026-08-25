# Google Sheets → Postgres / JSONL

A Meltano reference project that reads a CSV  and loads it into Postgres and JSONL files.

## → Read [reference/README.md](reference/README.md)

**[reference/](reference/) is the deliverable**: a self-contained, from-scratch working
copy of this project, with the exact command sequence, the full `meltano.yml`, the
`.env.example`, and every gotcha hit while building it. It has been reproduced from zero
against a brand-new Postgres cluster.

Start there. This top level is the original working copy the reference was distilled from.

## Layout here

```
reference/                 the deliverable -- start here
pipelines/                 one file per pipeline (Matatika convention)
datastores/                maps a pipeline's destination label to a loader
meltano.yml                plugins + config; no jobs, no schedules
extract/                   pre-flight sheet check, OAuth helper
transform/                 SQL that unpivots the raw table into a tidy view
output/                    JSONL output (gitignored)
```

## Quick commands

```bash
meltano run tap-spreadsheets-anywhere target-postgres
meltano run tap-spreadsheets-anywhere target-jsonl
```
