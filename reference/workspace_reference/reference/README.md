# Engineer Allocations — Google Sheets → Postgres / JSONL

A complete, reproducible Meltano project that reads a Google Sheet as CSV over HTTPS and
loads it to two destinations. Everything needed to rebuild it from nothing is in this
folder and this file.

Two pipelines, declared as one file each under [pipelines/](pipelines/):

| Pipeline | Extractor | Destination |
|---|---|---|
| `spreadsheets-anywhere.yml` | `tap-spreadsheets-anywhere` | `Warehouse` → Postgres |
| `spreadsheets-anywhere-jsonl.yml` | `tap-spreadsheets-anywhere` | `LocalFiles` → `output/*.jsonl` |

Source: the [engineer allocation roster](https://docs.google.com/spreadsheets/d/16c6KRvb4Vo7-JVEAxPYPprvOJT9uWDRBUiEqpl2Q-40/edit?gid=0),
shared *Anyone with the link*. No credentials are used.

---

## 1. File layout

```
reference/
├── meltano.yml                      plugins + config (no jobs, no schedules)
├── workspace.yml                    declares pipeline/datastore/plugin paths
├── .env.example                     secret template -> copy to .env
├── .gitignore
│
├── pipelines/                       one file per pipeline
│   ├── spreadsheets-anywhere.yml         tap + Warehouse
│   └── spreadsheets-anywhere-jsonl.yml   tap + LocalFiles
│
├── datastores/                      names a loader, so pipelines reference a label
│   ├── Warehouse.yml                     -> loaders/target-postgres--meltanolabs
│   └── LocalFiles.yml                    -> loaders/target-jsonl--andyh1203
│
├── extract/
│   └── check_sheet_access.py        pre-flight: is the sheet readable?
│
├── transform/
│   └── engineer_allocations_tidy.sql   unpivots the raw table into a tidy view
│
├── orchestrate/warehouse/
│   ├── pg.sh                        start/stop a local Postgres (no Docker needed)
│   ├── docker-compose.yml           Docker alternative, same host/port/user/db
│   └── initdb/01-schemas.sql        creates the `raw` schema in the Docker path
│
├── output/                          JSONL lands here (gitignored)
├── analyze/  load/  notebook/       standard Meltano dirs, unused
│
└── (generated, gitignored)
    ├── .meltano/                    plugin venvs + run artifacts
    ├── .pgdata/                     the Postgres cluster's data directory
    └── plugins/                     lock files, written by `meltano install`
```

## 2. Prerequisites

- **Meltano 4.x** — `pipx install meltano` or `uv tool install meltano`. Built on 4.2.0.
- **Python 3.12** with `PyYAML` (the pre-flight check imports it).
- **A Postgres server.** You do *not* need to install one — step 3 below builds a
  private cluster from a pip package. Docker is optional.
- Network access to `docs.google.com`, PyPI, and GitHub.

## 3. Exact command sequence

From inside this folder, in order. Nothing is hidden in a prior step.

```bash
# 1. Install the PostgreSQL 16 server binaries as a pip package (once per machine).
#    This needs no sudo and no Docker -- the cluster runs as your own user.
uv venv ~/.local/share/pg-warehouse/venv --python 3.12
VIRTUAL_ENV=~/.local/share/pg-warehouse/venv uv pip install pgserver

# 2. Boot the warehouse. On first run this initdb's a cluster into ./.pgdata,
#    creates the `meltano` role, the `warehouse` database, and the `raw` schema.
./orchestrate/warehouse/pg.sh start

# 3. Configuration. .env.example ships with working values for the sheet below,
#    so a plain copy is enough to reproduce this project. Edit it to point at
#    your own sheet. Every value is required -- see gotcha 9.
cp .env.example .env

# 4. Install the extractor and both loaders declared in meltano.yml.
meltano install

# 5. Pre-flight: confirm the sheet is publicly readable and the config is sane.
python3 extract/check_sheet_access.py

# 6. Pipeline 1 -- Google Sheets -> Postgres.
meltano run tap-spreadsheets-anywhere target-postgres

# 7. Pipeline 2 -- Google Sheets -> JSONL files.
meltano run tap-spreadsheets-anywhere target-jsonl

# 8. Build the tidy view over the raw table.
./orchestrate/warehouse/pg.sh psql -f transform/engineer_allocations_tidy.sql

# 9. Verify.
./orchestrate/warehouse/pg.sh psql -c "select count(*) from raw.engineer_allocations_raw;"
./orchestrate/warehouse/pg.sh psql -c "select * from raw.engineer_allocations limit 10;"
wc -l output/engineer_allocations_raw.jsonl
```

Expected at the end: **10 rows** in `raw.engineer_allocations_raw`, **60 rows** in the
`raw.engineer_allocations` view, **10 lines** in the JSONL file.

To run both destinations in one command, repeat the tap — see gotcha 11:

```bash
meltano run tap-spreadsheets-anywhere target-postgres \
            tap-spreadsheets-anywhere target-jsonl
```

### Warehouse commands

```bash
./orchestrate/warehouse/pg.sh start|stop|restart|status|logs
./orchestrate/warehouse/pg.sh psql                      # interactive
./orchestrate/warehouse/pg.sh psql -c "select 1"        # one-shot
```

Connection: `postgresql://meltano:meltano@localhost:5432/warehouse`, schema `raw`.
Override with `WAREHOUSE_PORT`, `WAREHOUSE_DB`, `WAREHOUSE_USER`, `WAREHOUSE_PASSWORD`
(e.g. `WAREHOUSE_PORT=5460 ./orchestrate/warehouse/pg.sh start` to sidestep a port clash).

## 4. `meltano.yml`

```yaml
default_environment: dev
project_id: engineer-allocations-reference

plugins:
  extractors:
  - name: tap-spreadsheets-anywhere
    variant: ets
    # PINNED DELIBERATELY -- see gotcha 3.
    pip_url: git+https://github.com/ets/tap-spreadsheets-anywhere.git@a780e6b551ac2a19692ae4e0726b381774e621c1
    config:
      tables:
      - name: engineer_allocations_raw
        # Sheet identity comes from .env, so this file holds no environment-specific
        # values and the same commit can point at a different sheet.
        path: https://docs.google.com/spreadsheets/d/${TAP_GOOGLE_SHEET_ID}/export?format=csv&gid=${TAP_GOOGLE_SHEET_GID}&filename=
        pattern: engineer_allocations.csv
        format: csv
        start_date: '2000-01-01T00:00:00Z'
        key_properties:
        - _smart_source_lineno      # see gotcha 8
        prefer_schema_as_string: true
        delimiter: ','
        quotechar: '"'
        field_names:                # col_01 .. col_21, see gotcha 15
        - col_01
        # ... through ...
        - col_21

  loaders:
  - name: target-postgres
    variant: meltanolabs
    pip_url: meltanolabs-target-postgres
    config:
      host: localhost
      port: 5432
      user: meltano
      database: warehouse
      default_target_schema: raw
      add_record_metadata: true
      # password from .env / TARGET_POSTGRES_PASSWORD

  - name: target-jsonl
    variant: andyh1203
    pip_url: target-jsonl
    config:
      destination_path: output

environments:
- name: dev
- name: staging
- name: prod
```

There is **no `jobs:` and no `schedules:` block** — pipelines are the `pipelines/*.yml`
files, consumed by the Matatika platform. Locally, invoke a tap/target pair directly as
in step 6.

The full file, including all 21 `field_names`, is [meltano.yml](meltano.yml).

## 5. `.env.example`

`meltano.yml` contains no environment-specific values. The sheet's identity and the
warehouse password both come from `.env`, so the same commit can be pointed at a
different spreadsheet by editing one file that is never committed.

```bash
# Copy to .env (which is gitignored) and fill in every value.
#
#   cp .env.example .env
#
# Nothing here is optional -- a blank value expands to an empty string and
# silently produces a malformed URL. See gotcha 9.

# ---------------------------------------------------------------------------
# Source: Google Sheets
# ---------------------------------------------------------------------------
# From the sheet's URL:
#   https://docs.google.com/spreadsheets/d/<TAP_GOOGLE_SHEET_ID>/edit?gid=<TAP_GOOGLE_SHEET_GID>
#
# The sheet must be shared "Anyone with the link" -- this extractor sends no
# credentials on HTTPS requests (gotcha 10).
TAP_GOOGLE_SHEET_ID=16c6KRvb4Vo7-JVEAxPYPprvOJT9uWDRBUiEqpl2Q-40
TAP_GOOGLE_SHEET_GID=0

# ---------------------------------------------------------------------------
# Destination: Postgres warehouse
# ---------------------------------------------------------------------------
# Must match the password orchestrate/warehouse/pg.sh created (default: meltano).
TARGET_POSTGRES_PASSWORD=meltano
```

Only `TARGET_POSTGRES_PASSWORD` is a genuine secret; the sheet ID is public. Both live
here so that nothing environment-specific sits in tracked config.

A note on the names: `TARGET_POSTGRES_PASSWORD` **is** a Meltano setting — Meltano derives
`TARGET_POSTGRES_PASSWORD` from the `password` setting on `target-postgres` and injects it
automatically. `TAP_GOOGLE_SHEET_ID` and `TAP_GOOGLE_SHEET_GID` are **not** settings of any
plugin; they are plain variables that `meltano.yml` interpolates with `${...}`. The `TAP_`
prefix is convention only, so don't go looking for a matching plugin setting. (Avoid
installing a plugin literally named `tap-google` with a `sheet_id` setting — Meltano would
generate the same variable name and the two would collide.)

**Pointing at a different sheet** is then a two-line change in `.env` — take the ID and
`gid` from your sheet's URL, share it *Anyone with the link*, and re-run
`python3 extract/check_sheet_access.py`. You may also want to revisit `field_names` and
`key_properties` in `meltano.yml` if the new sheet's shape differs (gotchas 15 and 8).

## 6. Pipelines and datastores

```yaml
# pipelines/spreadsheets-anywhere.yml
version: pipelines/v0.1
label: Engineer Allocations to Warehouse
timeout: 0
max_retries: 0
data_components:
- tap-spreadsheets-anywhere
- Warehouse
```

```yaml
# datastores/Warehouse.yml
version: datastores/v0.1
name: Warehouse
data_plugin: loaders/target-postgres--meltanolabs
```

A pipeline lists `data_components`: the extractor by plugin name, the destination by
**datastore label**. The datastore is an indirection over a loader, so swapping Postgres
for something else is a one-line change in `datastores/Warehouse.yml` and no pipeline
file changes. `data_plugin` must match a lock file path under `plugins/`.

## 7. Discovering streams

`meltano discover` **does not exist in Meltano 4** — it was removed. Use these instead.

### What streams and columns does the tap expose?

```bash
meltano select tap-spreadsheets-anywhere --list --all
```

For this project that reports one stream, `engineer_allocations_raw`, with 24
properties — `col_01`..`col_21` plus three `_smart_source_*` metadata columns:

```
Legend:
	selected
	excluded
	automatic
	unsupported

Enabled patterns:
	*.*

Selected properties:
	[automatic  ] engineer_allocations_raw._smart_source_bucket
	[automatic  ] engineer_allocations_raw._smart_source_file
	[automatic  ] engineer_allocations_raw._smart_source_lineno
	[automatic  ] engineer_allocations_raw.col_01
	...
	[automatic  ] engineer_allocations_raw.col_21
```

`--all` includes properties excluded by the current patterns; drop it to see only what
would actually be extracted. Everything shows as `automatic` here because the default
`*.*` pattern selects the whole stream.

### The raw Singer catalog

```bash
meltano invoke tap-spreadsheets-anywhere --discover
```

Prints the catalog JSON the tap generates by sampling the source — the authoritative
answer for stream names, inferred types, and key properties. Useful for confirming
`key_properties` landed:

```bash
meltano invoke tap-spreadsheets-anywhere --discover \
  | python3 -c "import json,sys; c=json.load(sys.stdin); \
      print([(s['stream'], s['key_properties']) for s in c['streams']])"
# [('engineer_allocations_raw', ['_smart_source_lineno'])]
```

Note this tap discovers by **downloading and sampling the file**, so it needs the sheet
reachable — it is not a cheap metadata call. It logs
`Sampling engineer_allocations.csv (1000 records, every 5th record)`.

### Changing what gets extracted

Selection patterns are written into `meltano.yml`, so these commands **modify the
project**:

```bash
# Only the data columns, dropping the tap's metadata columns
meltano select tap-spreadsheets-anywhere engineer_allocations_raw "col_*"

# Or exclude specific properties
meltano select tap-spreadsheets-anywhere --exclude engineer_allocations_raw "_smart_source_bucket"

# Review, then undo by deleting the `select:` block from meltano.yml
meltano select tap-spreadsheets-anywhere --list
```

Careful: excluding `_smart_source_lineno` would remove the primary key and re-runs would
start appending duplicates (gotcha 8).

### Resolved configuration

```bash
# Every setting, its env var, and where the current value came from
meltano config list --plugin-type extractor tap-spreadsheets-anywhere
meltano config list --plugin-type loader target-postgres

# The config JSON exactly as the plugin will receive it
meltano config print --plugin-type extractor tap-spreadsheets-anywhere
meltano --unsafe config print --plugin-type loader target-postgres   # reveal secrets
```

### Finding plugins to add

```bash
meltano hub ping                    # is the Hub reachable?
meltano add tap-google-sheets       # default variant
meltano add target-postgres --variant meltanolabs
```

Browse [hub.meltano.com](https://hub.meltano.com) for the catalogue and each plugin's
variants and settings.

## 8. The data: why two tables

The sheet is not a flat table:

```
row 1   Engineer | w/c 03/08 (merged across 10 cols) | w/c 10/08 (merged across 10)
row 2            | Mon (AM) | Mon (PM) | ... | Fri (PM) | Mon (AM) | ...
rows 3+ Dan      | IFG/CitySprint | IFG | ...
        (blank row)
        Additional        <- a second logical table starts here
        Dan      | ...notes...
```

Two header rows, merged cells, two stacked logical tables. So:

- **`raw.engineer_allocations_raw`** — the sheet verbatim. 10 rows, 21 text columns
  `col_01`..`col_21`, nothing skipped or renamed. Header rows are kept *as data*, so
  nothing is lost, including the week banners.

- **`raw.engineer_allocations`** — the tidy view from
  [transform/engineer_allocations_tidy.sql](transform/engineer_allocations_tidy.sql).
  One row per engineer per half-day: `engineer`, `week_commencing`, `day_of_week`,
  `session`, `allocation`. 3 engineers x 2 weeks x 10 slots = 60 rows. It finds the
  header and `Additional` rows by their **marker text**, not hardcoded line numbers, so
  it survives rows being added, and it excludes the notes block.

```sql
select week_commencing, allocation, count(*) as half_days
from raw.engineer_allocations
where allocation is not null
group by 1, 2 order by 1, half_days desc;
```

## 9. Gotchas

Every one of these was hit while building this. They are the reason the config looks the
way it does.

### Environment

**1. Docker was unusable.** The `docker` CLI resolved to Docker Desktop on Windows but
was not exposed to the WSL 2 distro (`The command 'docker' could not be found in this
WSL 2 distro`). Fix: enable *Docker Desktop → Settings → Resources → WSL Integration*,
or use `pg.sh`, which needs no Docker at all.

**2. No Postgres server and no passwordless sudo.** `/usr/bin/psql` existed but
`/usr/lib/postgresql/18/bin` held only *client* binaries — no `initdb`, no `postgres` —
and `apt install` needed an interactive password. Fix: the `pgserver` pip package ships
PostgreSQL 16 server binaries as a wheel, so a cluster can be initdb'd and run entirely
as an unprivileged user.

**3. The tap's `main` branch does not install.** `setup.py` is missing a comma, so
`install_requires` contains `jsonpath-ng>=1.5.3pyarrow>=5.0.0` — an invalid specifier
that hard-fails `pip install`. The Meltano Hub points `pip_url` at git HEAD, so a plain
`meltano add tap-spreadsheets-anywhere` fails. Fix: pin `pip_url` to commit
`a780e6b551ac2a19692ae4e0726b381774e621c1`. **Do not move the pin to `main`** until
upstream fixes it.

**4. `meltano add` changed syntax in v4.** `meltano add extractor tap-x` now errors with
`Utility 'extractor' is not known to Meltano`. Use `meltano add tap-x`, or
`meltano add --plugin-type extractor tap-x`.

**5. `version: 1` in `meltano.yml` is deprecated** in 4.2 and emits a warning on every
command. Omit it.

### The Google Sheets URL

**6. The tap builds its request as `path` + `"/"` + `pattern`** — always, with no way to
suppress the slash. Fix: put the entire export URL in `path` and end it with a dummy
`&filename=` parameter that swallows the slash. Google ignores unknown query params.

**7. `pattern` is compiled as a regex and matched against itself.** If it contains regex
metacharacters the self-match fails, the tap resolves **0 files, syncs 0 rows, and exits
successfully** — no error anywhere. `pattern: tq?tqx=out:csv` is silently fatal. Fix:
keep `pattern` a plain filename. `extract/check_sheet_access.py` explicitly guards this.

**8. Google's CSV export returns no `last-modified` header**, so the tap logs
`URL did not return a last-modified header so using current date and time` and treats
the file as changed on every run. Without a primary key that appends duplicates forever.
Fix: `key_properties: [_smart_source_lineno]` — the line number within the file, stable
across runs, so `target-postgres` upserts. Verified: three consecutive runs, still 10
rows.

**9. An unset `.env` variable expands to an empty string, silently.** `meltano.yml`
interpolates `${TAP_GOOGLE_SHEET_ID}` and `${TAP_GOOGLE_SHEET_GID}`. Meltano substitutes
partial values inside a string correctly — including nested under `tables` — but if a
variable is missing it inserts nothing and reports no error, so the URL becomes
`https://docs.google.com/spreadsheets/d//export?...` and the failure surfaces later as a
confusing HTTP error. Fix: copy `.env.example` verbatim and fill in every value.
`extract/check_sheet_access.py` names any variable that is unset or empty before it
attempts a fetch.

**10. Private sheets are impossible with this tap.** For `http`/`https` it calls bare
`requests.get(url)` and bare `smart_open.open(uri)` — no headers, no auth, no
`transport_params`. Only its `azure` scheme has a credential hook, so there is nowhere to
inject a Google token, and no `.env` variable can help. A sheet that is not
link-shared returns `HTTP 401` on every URL form, including `/edit`. Fix: either share it
*Anyone with the link*, or switch to `tap-google-sheets` (variant `matatika`), which uses
the Sheets API with OAuth and addresses tabs by **name**, not `gid`.

### Meltano CLI

**11. `meltano run tap-x target-a target-b` does not fan out.** It fails with
`BlockSetValidationError: Unknown command type or bad block sequence at index 3`. A block
is exactly one tap and one target. Fix: repeat the tap —
`meltano run tap-x target-a tap-x target-b`.

**12. `meltano discover` was removed in Meltano 4.** Use
`meltano select <tap> --list --all` for streams and properties, or
`meltano invoke <tap> --discover` for the raw Singer catalog.

**13. `meltano config` argument order is subcommand-first.**
`meltano config target-postgres list` fails with `No such command 'target-postgres'`.
Correct: `meltano config list --plugin-type loader target-postgres`, and likewise
`meltano config print --plugin-type extractor tap-spreadsheets-anywhere`.

**14. `meltano config test` does not work for `target-postgres` here** — it raises
`ProcessLookupError`. Test the connection with
`./orchestrate/warehouse/pg.sh psql -c "select 1"` instead.

### Data shape and loaders

**15. `field_names` must cover every column.** The sheet's two-row merged header means
the CSV's first row is not usable as column names, and the day headers repeat across the
two week blocks, so they are not unique. Fix: declare explicit `col_01`..`col_21` and
keep all rows as data. Anything beyond the declared names is silently dropped — the
pre-flight check warns when the sheet is wider than the config.

**16. `target-jsonl` appends; it does not truncate or dedupe.** Three runs produced 30
lines from 10 rows. Unlike Postgres, the primary key is ignored. Fix: delete the file
before a run, or set `do_timestamp_file: true` for one timestamped file per run.

### Connecting to the warehouse

**17. Port 5432 may already be taken by another Postgres.** On the build machine a second
server was listening on the Windows host, so a Windows GUI connecting to `localhost:5432`
reached *that* server and reported `password authentication failed for user "meltano"` —
the credentials were fine, the server was wrong. Fix: connect from inside WSL, or use
`WAREHOUSE_PORT=5433 ./orchestrate/warehouse/pg.sh start` and set `port` in `meltano.yml`
to match.

**18. `psql` without `-U` uses your OS username** and fails with
`password authentication failed for user "<you>"`. Fix: always pass `-U meltano`, or use
`./orchestrate/warehouse/pg.sh psql`, which cannot get it wrong.

**19. The cluster does not survive a reboot.** It is a user-owned process, not a system
service. After a restart, connections are refused until
`./orchestrate/warehouse/pg.sh start`. Data in `.pgdata/` is unaffected. Anything
scheduled must start the warehouse first:

```bash
0 7 * * * cd /path/to/reference && ./orchestrate/warehouse/pg.sh start \
  && meltano run tap-spreadsheets-anywhere target-postgres
```

**20. Nothing runs on a schedule.** No orchestrator is installed. The `pipelines/*.yml`
files carry no interval — scheduling is the platform's job, or cron's.

## 10. Reproduction record

This exact sequence was run in a clean copy of this folder, against a brand-new cluster
on port 5460, immediately before writing this document:

| Step | Result |
|---|---|
| `pg.sh start` (no existing `.pgdata`) | cluster initialised, role + db + `raw` schema created |
| `meltano install` | `Installed 3/3 plugins` |
| `check_sheet_access.py` | `OK 10 rows, 799 bytes, 21 columns` |
| `meltano run ... target-postgres` | `record_count 10` |
| `meltano run ... target-jsonl` | 10 lines in `output/` |
| `psql -f transform/...tidy.sql` | `CREATE VIEW` |
| `select count(*) ... _raw` | 10 |
| `select count(*) ... engineer_allocations` | 60 slots, 3 engineers |
| Spot-check vs source CSV | Dan's week-1 row matches exactly |
