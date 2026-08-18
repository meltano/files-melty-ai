# Connectors

Overview of Meltano connectors (extractors and loaders) plus per-connector setup, configuration, and troubleshooting notes for a set of specific connectors documented in depth.

## Overview

Meltano Cloud connectors move data in one of two directions: extractors pull data out of a source, and loaders push it into a destination. Each connector's documentation covers setup instructions, configuration options, and streams.

Meltano Hub (https://hub.meltano.com/) hosts the full catalog of community connectors beyond the ones documented in depth here.

The connectors covered below in depth are:

- Rakuten Advertising (extractor)
- Spreadsheets (IMAP) (extractor)
- Spreadsheets (Outlook) (extractor)
- Spreadsheets (SharePoint) (extractor)
- SurveyMonkey (extractor)
- Weather API (extractor)
- Zendesk (extractor)
- ClickHouse (loader)

---

### Rakuten Advertising

**Type:** Extractor

Rakuten Advertising is an affiliate marketing platform that connects advertisers with publishers to drive sales through performance-based partnerships. This tap extracts data from three API groups: the Core API (advertisers, events, partnerships, offers, coupons, product search, link locator data, etc.), the Advanced Reports API (payment history, advertiser payments, payment details), and the Reporting Platform (custom reports).

**At a glance**

| Property | Value |
|---|---|
| Authentication | Bearer Token, Security Token, Reporting Platform API Token |
| APIs | Core API, Advanced Reports API, Reporting Platform |
| Replication | Incremental and full-table |
| Incremental streams | Events, publisher contributed conversions |
| Reference data | Full-table replication |
| Custom reports | Supported through Reporting Platform |
| Multiple reports | Supported through comma-separated report keys |
| Reporting date types | `transaction`, `process` |
| Reporting region | `en` by default |

**What you can sync**

- Core API streams: Advertisers, Events, Advertiser search, Partnerships, Publisher contributed conversions, Offers, Commissioning lists, Coupons, Product search, Text links, Banner links, DRM links, Creative categories. Incremental replication applies to transaction-based streams (Events, Publisher contributed conversions); reference data streams use full-table replication.
- Advanced Reports API streams: Payment history, Advertiser payments v1, Payment details v1, Advertiser payments v2, Payment details v2. These require a separate Security Token.
- Reporting Platform: custom reports you've built in Rakuten Advertising. Each configured report key becomes a stream named `reporting_{report_key}` (e.g. `reporting_sales-and-activity-report`).

**Key config options**

| Setting | Type | Required / Default | Description |
|---|---|---|---|
| `auth_token` | string | required | Bearer Token for the Core API. Required for all Core API streams. |
| `security_token` | string | optional | Security Token for the Advanced Reports API. |
| `advanced_reports_pay_id` | string | optional | Payment ID required for advertiser payments streams using report IDs 2 and 22. |
| `advanced_reports_invoice_id` | string | optional | Invoice ID required for payment details streams using report IDs 3 and 23. |
| `advanced_reports_network_id` | integer | optional | Optional network ID filter. Valid values: `1`, `3`, `5`, `41`. |
| `reporting_api_token` | string | optional | API token for the Reporting Platform. Required for `reporting_*` streams. |
| `reporting_report_keys` | string | optional | Comma-separated report keys for the Reporting Platform. Each key becomes a separate stream. |
| `start_date` | string | optional | ISO 8601 earliest sync date, e.g. `2025-01-01T00:00:00Z`. Defaults to 6 months ago if unset. |
| `reporting_region` | string | `en` | Region code for the Reporting Platform API. |
| `reporting_date_type` | string | `transaction` | `transaction` or `process`. |

Credential requirements scale with what you need: Core API only needs `auth_token`; Advanced Reports needs `auth_token` + `security_token` (plus optional pay/invoice/network IDs); Reporting Platform needs `auth_token` + `reporting_api_token` + `reporting_report_keys`.

**Setup gotchas**

- Obtain the Bearer Token via `developers.rakutenadvertising.com` → **Manage > Applications**.
- The Security Token is found on the Advanced Reports page (or in the Advanced Reports API URL), separate from the Bearer Token.
- To find a Reporting Platform report key and token: open the report → dropdown next to **View report** → **Get API** → parse the URL `ran-reporting.rakutenmarketing.com/{region}/reports/{REPORT-KEY}/filters?...&token={API-TOKEN}`.
- When building a Reporting Platform report, set **Convert Currency to...** to **Do Not Convert**.
- Multiple reports: pass report keys as a comma-separated list, e.g. `revenue-report-by-day,sales-and-activity-report,product-success-report`.

---

### Spreadsheets (IMAP)

**Type:** Extractor

Syncs spreadsheet data from attachments in an IMAP mailbox. The tap connects to an IMAP mailbox, discovers email attachments based on configured table definitions, and extracts data from supported spreadsheet/structured file formats (CSV, JSON, JSONL, Excel, or auto-detected).

**At a glance**

| Property | Value |
|---|---|
| Authentication | Mailbox email address and password |
| Connection | IMAP |
| Supported formats | CSV, JSON, JSONL, Excel, or automatic detection |
| File selection | IMAP paths with glob pattern matching and regex filtering |
| Replication | File-based discovery with configurable start date |
| State-based discovery | Optional; recommended |
| CSV support | Custom delimiter and quote character |
| Excel support | Specific worksheet selection |
| Primary keys | File metadata or custom stream keys |
| Append-only | Supported |

**What you can sync**

Folders and emails are treated as directories, attachments as files. IMAP paths support globs, e.g.:

- `imap://<host>/*/*/` — all emails in all top-level folders
- `imap://<host>/INBOX/*/` — all emails in the inbox
- `imap://<host>/INBOX/*/*` — all attachments for emails in the inbox
- `imap://<host>/INBOX/*/*.csv` — all CSV attachments for emails in the inbox

**Key config — `tables` (array of table definitions)**

| Field | Type | Required / Default | Description |
|---|---|---|---|
| `name` | string | required | Stream name. |
| `path` | string | required | `imap://<host>/path/to/folder-or-emails`, supports glob matching. |
| `format` | string | required | `csv`, `json`, `jsonl`, `excel`, or `detect`. |
| `pattern` | string | required | Regex filter on resolved file names. Use `""` when `path` already filters sufficiently. |
| `start_date` | string | required | ISO-8601 date-time filtering files by last-modified timestamp. |
| `key_properties` | array of strings | required | Stream primary keys. Use meta-properties (`_smart_source_bucket`, `_smart_source_file`, `_smart_source_lineno`) when no clear key exists, or `[]` for append-only. |
| `encoding` | string | `utf-8` | File read encoding. |
| `state_based_discovery` | boolean | `false` | Sample files from the state bookmark rather than `start_date`. Recommended: `true`. |
| `skip_initial` | integer | `0` | Lines to skip when reading a file (useful for Excel). |
| `max_sampled_files` | integer | `50` | Files sampled during dynamic catalog discovery. |
| `max_sampling_read` | integer | `1000` | Lines sampled per file during discovery. |
| `sample_rate` | integer | `5` | Sample every Nth line during discovery. |
| `prefer_schema_as_string` | boolean | `false` | Skip type inference during sampling. Combine with `max_sampling_read: 1` for CSV to speed up discovery. |
| `delimiter` (csv only) | string | `,` | Value delimiter. |
| `quotechar` (csv only) | string | `"` | Quote character; set `detect` to auto-discover. |
| `worksheet_name` (excel only) | string | — | Specific worksheet; defaults to the sheet with the most data. |

Email settings: **Mailbox email address** and **Password** used to connect to the mailbox.

**Example table config**

```json
{
  "name": "connectors_split",
  "path": "imap://imap.example.com/INBOX/*/*.csv",
  "format": "csv",
  "pattern": "",
  "start_date": "2026-01-01T00:00:00Z",
  "key_properties": [
    "_smart_source_bucket",
    "_smart_source_file",
    "_smart_source_lineno"
  ]
}
```

**Setup gotchas**

- Uses dynamic catalog discovery to infer schema; tune with `state_based_discovery`, `max_sampled_files`, `max_sampling_read`, `sample_rate`, `prefer_schema_as_string`.
- Meta-property primary keys (`_smart_source_bucket`/`_smart_source_file`/`_smart_source_lineno`) are only safe for files that are effectively immutable — changes to file location/contents can cause duplicates or overwrites.
- If `format: detect` can't figure out the format, set it explicitly.

---

### Spreadsheets (Outlook)

**Type:** Extractor

Reads mail and attachments directly out of a single Office 365 mailbox via IMAP, using OAuth sign-in with the mailbox's own Microsoft account. Built for teams whose working data (spreadsheets, exports, reports) lands as email attachments.

**At a glance**

| Property | Value |
|---|---|
| Authentication | OAuth login (Sign in with Microsoft) |
| Streams | Configured per mailbox folder (not a fixed list) |
| Custom queries | Not supported |

**What you can sync:** attachments and message content from configured folders, scoped to what the signed-in account can see (never another mailbox).

**Prerequisites**

- A Microsoft/Office 365 account for the mailbox.
- IMAP enabled for that mailbox (an Exchange Online setting — check with IT; sync fails even after sign-in succeeds if IMAP is off).
- IT admin approval, in some organizations (see below).

**Key config — `tables` (array of table definitions)**

Same shape as Spreadsheets (IMAP): `name`, `path` (format `imap://imap.outlook.com/path/to/folder-or-emails`), `format`, `pattern`, `start_date`, `key_properties`, `encoding`, `state_based_discovery`, `skip_initial`, `max_sampled_files`, `max_sampling_read`, `sample_rate`, `prefer_schema_as_string`, plus `delimiter`/`quotechar` (CSV) and `worksheet_name` (Excel).

**Setup gotchas — IT admin consent**

Outlook access requests only `IMAP.AccessAsUser.All` (read access to the signed-in user's own mailbox) and `offline_access` (keeps scheduled syncs running without re-auth). Microsoft classifies `IMAP.AccessAsUser.All` as low impact, so most tenants allow self-consent — an admin prompt only appears if the org has tightened consent settings further than default. If prompted, IT grants consent via `Entra admin centre → Enterprise applications → Consent and permissions`, or via `Enterprise applications → Admin consent requests` if the tenant routes through a request queue. Once granted, other users in the org can connect without hitting the prompt.

---

### Spreadsheets (SharePoint)

**Type:** Extractor

Pulls spreadsheet and file data directly out of an organization's SharePoint sites via OAuth (Sign in with Microsoft), for teams that keep working data in Excel/CSV on SharePoint.

**At a glance**

| Property | Value |
|---|---|
| Authentication | OAuth login (Sign in with Microsoft) |
| Streams | Configured per site and folder path (not a fixed list) |
| Custom queries | Not supported |

**What you can sync:** Excel workbooks and CSV files in a SharePoint site's document libraries — anything the signed-in user could already open in a browser, nothing more.

**Prerequisites**

- Microsoft account access to the target site — must already be able to open the path in a browser.
- IT admin approval, in most organizations (see below) — the most common blocker for this connector.

**Key config — `tables` (array of table definitions)**

| Field | Type | Required / Default | Description |
|---|---|---|---|
| `name` | string | required | Stream name. |
| `path` | string | required | `sharepoint://<site_name>/path/to/dir`. |
| `format` | string | required | `csv`, `json`, `jsonl`, `excel`, or `detect`. |
| `pattern` | string | required | Regex filter on file names; `""` if `path` already filters sufficiently. |
| `start_date` | string | required | ISO-8601 date-time, filters on last-modified timestamp. |
| `key_properties` | array of strings | required | Stream primary keys; meta-properties or `[]` for append-only (same caveats as IMAP variants). |
| `encoding` | string | `utf-8` | File read encoding. |
| `skip_initial` | integer | `0` | Lines to skip (Excel). |
| `max_sampled_files` | integer | `50` | Files sampled during discovery. |
| `max_sampling_read` | integer | `1000` | Lines sampled per file. |
| `sample_rate` | integer | `5` | Sample every Nth line. |
| `prefer_schema_as_string` | boolean | `false` | Skip type inference during sampling. |
| `delimiter` (csv only) | string | `,` | Value delimiter. |
| `quotechar` (csv only) | string | `"` | Quote character; `detect` to auto-discover. |
| `worksheet_name` (excel only) | string | — | Specific worksheet; defaults to sheet with most data. |

Note: unlike the IMAP/Outlook variants, this connector has no `state_based_discovery` field listed.

**Setup gotchas — IT admin consent**

SharePoint access uses Microsoft Graph's `Sites.Read.All` and `Files.Read.All` permissions plus `offline_access`. Because these carry the broader `.All` suffix, Microsoft does not classify them as low impact, so SharePoint connections almost always require admin approval even in tenants that allow self-approval for minor apps — this is the single biggest reason a SharePoint connection stalls. Grant consent via `Entra admin centre → Enterprise applications → Consent and permissions`, or via the `Admin consent requests` queue if enabled. Once approved once, every user in the org can connect without re-prompting.

---

### SurveyMonkey

**Type:** Extractor

Syncs survey definitions, distribution data, and responses, pre-flattened into relational tables so no warehouse-specific SQL is needed to unnest nested survey/response data.

**At a glance**

| Property | Value |
|---|---|
| Authentication | OAuth login (Connect with SurveyMonkey) |
| Sync type | Mixed: some streams incremental, some full table |
| Streams | Fixed list |
| Custom queries | Not supported |

**Prerequisites**

- A SurveyMonkey account with access to the surveys to sync (no manual credential — sign in directly during setup). Connecting as a non-admin only syncs what that user can see.
- A paid SurveyMonkey plan for full per-question answer detail (`responses` and `response_answers` streams); Basic plans have limited response answer detail.

**Key config**

| Field | Type | Required / Default | Description |
|---|---|---|---|
| `start_date` | string | required | ISO-8601 date-time; earliest response date synced, used as the incremental bookmark for `responses`. |
| `api_url` | string (options) | `https://api.surveymonkey.com/v3` | Data-residency region: United States, Europe (EU), or Canada (CA). Wrong region causes auth/lookup failures. |

OAuth token management is automatic via the **Connect with SurveyMonkey** flow.

**Available streams:** `surveys`, `survey_details`, `collectors`, `recipients`, `responses`, `survey_pages`, `questions`, `question_headings`, `question_options`, `sub_questions`, `response_pages`, `response_answers`, `contacts` (requires `contacts_read` scope), `survey_categories`.

`responses`, `response_pages`, and `response_answers` sync incrementally on `date_modified`, bookmarked against Start Date. Every other stream is full-table and re-syncs completely each run.

**Setup gotchas**

- To backfill response history, lower the Start Date or reset the connection's sync state.
- Streams reflect current state only — not SCD type-2 history. If migrating from a tool with `_history` tables (e.g. Fivetran), valid-from/valid-to versioning must be layered in the warehouse (e.g. dbt snapshots), and can't be backfilled from before the first snapshot run.

---

### Weather API

**Type:** Extractor

WeatherAPI provides current conditions, forecasts, and historical weather data worldwide, queryable by city name, US ZIP, UK postcode, lat/long, IP address, and more.

**At a glance**

| Property | Value |
|---|---|
| Authentication | API Key |
| API | WeatherAPI REST API |
| Streams | `forecast`, `historical` |
| Replication | Full-table refresh for forecast; incremental for historical |
| Forecast range | 1-14 days |
| Historical replication key | `date` |
| Location formats | City name, US ZIP, UK/Canada postcode, lat/long, airport code, IP address, Search API ID |
| Multiple locations | Supported |
| Locations file | Supported |
| Bulk requests | Supported with eligible plans |
| Bulk request chunk size | 5-50 locations |

**Key config**

| Field | Type | Required / Default | Description |
|---|---|---|---|
| API Key | string | required | WeatherAPI API key. |
| Locations | array | — | One or more locations (various formats). Use Locations File for many locations. |
| Locations File | string | — | Path to a JSON file of locations; each entry has `location` and optional `custom_id`. |
| Start Date | string | — | `YYYY-MM-DD`; earliest date for `historical`. |
| End Date | string | yesterday | Latest date for `historical`, ISO format. |
| Forecast Days | integer | — | 1-14, days included in `forecast`. |
| Use Bulk Requests | boolean | `false` | Send all locations in one POST instead of per-location GETs. Requires Pro+/Business/Enterprise plan. Each location still counts as one API call. |
| Bulk Request Chunk Size | integer | — | 5-50 locations per bulk POST. Only applies when bulk requests enabled. |

Locations File format:
```json
[
  {
    "location": "90210",
    "custom_id": "beverly-hills"
  }
]
```

**Streams**

- `forecast`: full-table refresh, no replication key. One record per forecast day per location. Primary key: `location` + `date`. Includes nested hourly data (`hour` array) with temperature, wind, precipitation, humidity, etc.
- `historical`: incremental via `date`, starting from `start_date`. Shares schema with `forecast`. `End Date` defaults to yesterday if unset.

**Setup gotchas**

- Wrong Region/format for a location causes auth or lookup failures.
- Bulk requests require Pro+/Business/Enterprise plans; chunk size must be 5-50; each location still counts as one API call even in bulk mode.
- For many locations, prefer Locations File over the direct Locations setting.

---

### Zendesk

**Type:** Extractor

Zendesk Support is a customer service platform; this connector brings in ticketing data, support operations config, CX signals, and Help Center content.

**At a glance**

| Property | Value |
|---|---|
| Authentication | API key / token |
| Sync type | Mixed: some streams incremental, some full table |
| Streams | Fixed list |
| Custom queries | Not supported |

**Prerequisites**

- A Zendesk account with API token access (the connector authenticates as an agent via API token, not a full sign-in flow).
- Zendesk subdomain and agent email address.
- API token generated via **Admin Center → Apps and integrations → Zendesk API**.

**Key config**

| Field | Type | Required / Default | Description |
|---|---|---|---|
| `subdomain` | string | required | The `mycompany` part of `mycompany.zendesk.com`. |
| `email` | string | required with token auth | Agent email, used with `api_token`. |
| `api_token` | string | required with token auth | Generated in Admin Center → Apps and integrations → Zendesk API. |
| `start_date` | string | required | ISO-8601 earliest record date. |

**Streams**

Incremental (bookmark carried between syncs): `tickets` (`updated_at`), `users` (`updated_at`), `organizations` (`updated_at`), `ticket_metric_events` (`time`).

Full-table (re-synced every run): `automations`, `brands`, `custom_roles`, `group_memberships`, `groups`, `macros`, `organization_fields`, `organization_memberships`, `satisfaction_ratings`, `schedules`, `sla_policies`, `tags`, `ticket_fields`, `ticket_forms` (Enterprise-only, skipped gracefully if unavailable), `ticket_metrics`, `triggers`, `user_fields`, `user_identities` (child of `users`), `views`.

Help Center streams (skipped gracefully if Guide isn't enabled): `articles`, `categories`, `posts`, `sections`, `topics`.

**Setup gotchas**

- `ticket_forms` requires an Enterprise plan and is skipped gracefully otherwise.
- Help Center streams require Guide enabled and are skipped gracefully otherwise.

---

### ClickHouse

**Type:** Loader

ClickHouse is a high-performance, column-oriented OLAP SQL database. As a Meltano data store, it can serve as loader destination, state backend, and dbt transform target simultaneously.

**At a glance**

| Property | Value |
|---|---|
| Authentication | Username and password |
| Connection | HTTP, native, or asynchronous native driver |
| TLS | Supported; recommended for public endpoints, required for ClickHouse Cloud |
| Data model | ClickHouse database is the schema (no separate schema namespace) |
| Loading | Append-only, upsert, or overwrite |
| Table engines | `MergeTree`, `ReplacingMergeTree`, `Replicated*` and others |
| SSH tunnel | Supported |

**Prerequisites**

- A running ClickHouse instance (Cloud or self-managed): host, port, username/password, target database.
- Network access from Meltano; TLS for public endpoints; ClickHouse Cloud uses HTTPS on port 8443.
- Admin access if creating the database/service user/grants.
- ClickHouse server 22.8+ (earlier versions may fail with the default native bulk-insert path due to compression compatibility).

**Setup**

Create a dedicated service user:
```sql
CREATE DATABASE IF NOT EXISTS meltano;

CREATE USER IF NOT EXISTS import_runner
IDENTIFIED WITH sha256_password BY '<strong-password>';

GRANT SELECT, INSERT, ALTER, CREATE TABLE, DROP TABLE, OPTIMIZE
ON meltano.* TO import_runner;
```

Restrict inbound access to Meltano's static egress IP: `51.137.148.226` (add `51.137.148.226/32` to the ClickHouse Cloud IP Access List; avoid `0.0.0.0/0`).

**Key config**

| Field | Type | Required / Default | Description |
|---|---|---|---|
| SQLAlchemy URL | string | — | Full connection string; takes precedence over individual settings. |
| Host | string | required | ClickHouse host. |
| Port | integer | `8123` | `8123` HTTP, `8443` secure HTTP, `9000` native driver. |
| Driver | string | `http` | `http`, `native`, or `asynch`. |
| Username | string | `default` | ClickHouse username. |
| Password | string | required | ClickHouse password. |
| Database | string | required | Target database (acts as schema). |
| Secure (TLS) | boolean | `false` | Enable for ClickHouse Cloud / TLS endpoints. |
| Verify SSL/TLS | boolean | `true` | Verify server cert when secure. |
| SSH Tunnel Enable | boolean | `false` | Enable bastion tunnel. |
| SSH Tunnel Host / Port / Private Key / Private Key Password / Username | — | — | Bastion connection details. |
| Default Target Schema | string | — | Overrides target database; prefer setting Database directly. |
| Engine Type | string | `ReplacingMergeTree` | `MergeTree` for append-only, `ReplacingMergeTree` for upsert dedup. |
| Table Name | string | stream name | Target table name. |
| Table Path | string | — | Required for replicated engines; supports `$table_name`. |
| Replica Name | string | — | Required for `Replicated*` engines. |
| Cluster Name | string | — | Used for `ON CLUSTER` table creation. |
| Order By Keys | array | stream key | `ORDER BY` columns; dedup key for `ReplacingMergeTree`. |
| Optimize After Load | boolean | `false` | Runs `OPTIMIZE TABLE` after load; required to collapse `ReplacingMergeTree` upsert duplicates. |
| Async Insert | boolean | `false` | Server-side async inserts for the HTTP driver; useful for high-volume small batches. |
| Load Method | string | `upsert` | `append-only`, `upsert`, or `overwrite`. |
| Hard Delete | boolean | — | Controls handling of records no longer matching an activate version. |
| Add Record Metadata | boolean | `true` | Adds `_sdc_*` columns; required for activate-version / hard-delete. |
| Process ACTIVATE_VERSION messages | boolean | — | Whether to process ACTIVATE_VERSION messages. |
| Batch Size Rows | integer | `10000` | Rows per load batch. |
| Validate Records | boolean | — | Validate incoming stream schema. |
| Flattening Enabled / Max Depth | — | — | Nested property flattening. |
| Stream Maps / User Stream Map Configuration | object | — | Inline transformation config. |
| Faker Locale / Faker Seed | string | — | Faker output config. |

**Load methods**

- **Append-only**: writes every record; recommended for immutable event/time-series and incremental syncs; avoids `OPTIMIZE TABLE` cost. `load_method = append-only`, `engine_type = MergeTree`.
- **Upsert**: emulates row updates via `ReplacingMergeTree` (`ORDER BY` key = dedup key) plus `OPTIMIZE TABLE`. `load_method = upsert`, `engine_type = ReplacingMergeTree`, `optimize_after = true`. Can be significantly more expensive than append-only on large tables since `OPTIMIZE` can rewrite whole partitions.
- **Overwrite**: deletes existing records, inserts incoming data.

**Using ClickHouse as a full data store**

When connected as a full data store: `target-clickhouse` loads data, pipeline state is stored automatically (no separate state backend needed — Meltano derives it from the store connection, storing state in `meltano.state`), and `dbt-clickhouse` can run transforms against the same database/user.

**Setup gotchas / troubleshooting**

- Connection refused/timeout: check Meltano's egress IP is allow-listed and the port matches the driver (`8443` secure HTTP, `8123` plain HTTP, `9000` native).
- Table/database mismatch: don't set Database and Default Target Schema to different values — ClickHouse uses the database as its schema, so set Database directly and leave Default Target Schema unset.
- Slow upsert loads: `optimize_after` runs `OPTIMIZE TABLE`, which can rewrite partitions — switch to append-only if key-level dedup isn't needed.
- Duplicate rows after upsert: `ReplacingMergeTree` dedup is eventual; enable `optimize_after` or query with `FINAL`.
- ClickHouse Cloud connection failures: confirm TLS enabled, port `8443`, and Meltano's IP present in the Cloud IP Access List.
