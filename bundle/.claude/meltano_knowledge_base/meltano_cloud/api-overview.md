# Meltano Cloud API Overview

Reference documentation for the Meltano Cloud REST API — Matatika's managed data platform built on Meltano. This knowledge base is derived from the Docusaurus API reference under `reference/cloud/api/` and is intended for use as context by AI coding agents and by humans.

This file covers API basics (base path, authentication, errors, link conventions, pagination, searching). Full per-resource endpoint documentation lives in `api-resources.md`.

---

## Base Path

All endpoints are rooted at `/api`, e.g. `/api/workspaces`, `/api/pipelines/{pipeline-id}`. A small number of resource-oriented endpoints (used mainly for dataset-scoped alerts and search) are documented in source without the `/api` prefix (e.g. `/datasets/{dataset-id}/alerts`) — treat these as equivalent to their `/api`-rooted counterparts unless testing shows otherwise.

## Authentication

The API supports:

- **Bearer token** authentication — obtain a token from Meltano Cloud (e.g. via `https://app.meltano.com/api-key`) and send it as a Bearer token on requests.
- **API keys** — an alternate authentication method using a client ID and secret pair (see [API Keys](api-resources.md#api-keys)), useful for machine-to-machine access without a user's personal bearer token.

Most endpoints additionally require the authenticated profile to satisfy resource-specific prerequisites (e.g. "must be a member of the workspace", "must be an owner of the account") — these are listed per-endpoint in `api-resources.md`.

## Response Format

Collections and single resources are returned as `application/hal+json` — standard JSON bodies augmented with HAL links describing available actions on the resource (see Link Relations and Actions, below). Most resource docs describe both the returned object shape and its "with HAL links" wrapping; the object field tables in `api-resources.md` describe the core JSON payload.

## Errors

The API returns standard HTTP status codes, plus a consistent JSON error structure across all failure scenarios.

**General meaning of status code ranges:**
- `2xx` — success
- `4xx` — error with the request
- `5xx` — issue with the Meltano Cloud API itself

**Status codes used across the API:**

| Status | Text | Description |
|---|---|---|
| `200` | OK | The request was accepted and existing or modified data was returned. |
| `201` | Created | The request was accepted and new data was added. |
| `202` | Accepted | The request was accepted and will be processed; new data will be added once processing completes. |
| `400` | Bad Request | The request body contained malformed content of type `application/hal+json`. |
| `401` | Unauthorized | The request does not have a valid API token. |
| `403` | Forbidden | The request has a valid API token, but is not permitted. |
| `404` | Not Found | The request URI is invalid. |
| `405` | Method Not Allowed | The request HTTP method is not supported by the endpoint. |
| `409` | Conflict | The request conflicts with the current state of the server. |
| `503` | Service Unavailable | The API has encountered an error; try again later. |

**Validation error schema (`4xx` responses):**

| Path | JSON Type | Format | Description |
|---|---|---|---|
| `timestamp` | `string` | ISO 8601 timestamp | The instant when the error was encountered |
| `status` | `number` | HTTP status code | The error response code |
| `error` | `string` | | The error response text |
| `errors` | `object[]` | | Error object collection (one entry per failing field) |
| `message` | `string` | | The error description |
| `path` | `string` | | The request path that resulted in the thrown error(s) |

## Link Relations, Pagination, and Actions

The API uses HAL-style link relations throughout responses to communicate what actions are currently available on a resource, rather than requiring the client to hardcode URL construction logic.

### Item and Collection Relations

Every resource type exposes an item relation (singular) and a collection relation (plural) in its links:

| Resource | Item relation | Collection relation |
|---|---|---|
| Profile | `profile` | `profiles` |
| Workspace | `workspace` | `workspaces` |
| Invitation | `invitation` | `invitations` |
| Member | `member` | `members` |
| Administrator | `administrator` | `administrators` |
| Dataset | `dataset` | `datasets` |
| Channel | `channel` | `channels` |
| Comment | `comment` | `comments` |
| Tag | `tag` | `tags` |
| Dataplugin | `dataplugin` | `dataplugins` |
| Datastore | `datastore` | `datastores` |
| Pipeline | `pipeline` | `pipelines` |
| Job | `job` | `jobs` |
| Subscription | `subscription` | `subscriptions` |
| Notification | `notification` | `notifications` |
| API Key | `apikey` | `apikeys` |

A link formed entirely from an item or collection relation accepts a `GET` and returns the respective resource (`200 OK`).

### Paging, Sizing, and Sorting

Collection link relations accept these query parameters to shape the response payload:

| Query Parameter | Description | Syntax | Example |
|---|---|---|---|
| `page` | The page of the collection | `page={page-number}` | `?page=1` |
| `size` | The number of elements per page | `size={number-of-elements}` | `?size=20` |
| `sort` | The property to sort by, ascending (`asc`) or descending (`desc`) | `sort={property-name},(asc\|desc)` | `?sort=name,asc` |

### Searching and Filtering

A `search` action link indicates the endpoint accepts the `q` query parameter to filter response content. Supported filter types:

| Type | Description | Syntax | Example |
|---|---|---|---|
| Free text | Free text to filter by | `{free-text}` | `?q=data%20insights` |
| Channel | Filter by channel | `in:{channel-name}` | `?q=in:meltano` |
| Tag | Filter by tag | `tag:{tag-name}` | `?q=tag:jupyternotebook` |

Multiple filters — including multiple of the same type — can be combined in one query:

```
?q=data%20insights in:meltano tag:jupyternotebook
?tag:ai tag:deeplearning tag:machinelearning
```

### Actions

Actions are verb phrases describing the behavior of an HTTP transaction. A link relation is formed from an action verb alone, or combined with a resource relation as `"{action} {resource-relation}"` (e.g. `"update workspace"`, `"create pipeline"`, `"new job"`).

| Action | Method | Expected success response | Meaning |
|---|---|---|---|
| `latest` | GET | `200 OK` | Return the latest resource |
| `search` | GET | `200 OK` | Return a filtered view of the resource |
| `self` | GET | `200 OK` | Return the current resource |
| `new` | POST | `200 OK` | Initialise a new resource |
| `publish` | POST | `201 Created` or `200 OK` | Publish data into a resource |
| `validate` | POST | `200 OK` | Validate a resource |
| `verify` | POST | `200 OK` | Verify a resource |
| `add` | PUT | `200 OK` | Add a new resource |
| `create` | PUT | `201 Created` or `202 Accepted` | Create a new resource |
| `draft` | PUT | `200 OK` or `201 Created` | Create or update a draft resource |
| `make-default` | PUT | `200 OK` | Set a resource within a collection as default |
| `update` | PUT | `200 OK` | Update a resource |
| `withdraw` | PUT | `200 OK` | Withdraw a resource |
| `edit` | PATCH | `200 OK` | Edit a resource |
| `delete` | DELETE | `204 No Content` | Delete a resource |

Many resources follow an **initialise → create/update** pattern: a `POST .../new` (or similar) call initialises a draft resource and returns an `id`, and a subsequent `PUT` to the resource's specific `{id}` URL creates or finalises it. Look for this pairing in the per-resource endpoint lists.

## Postman Collection

A fully-tested Postman collection covering every documented request is maintained and importable directly from the live docs site (collection URL is generated per-deployment as `{docs-site-origin}/reference/cloud/api/postman_collection.json`, so there is no fixed static URL to record here). The collection auto-populates `{{profile-id}}` and `{{workspace-id}}` variables from a configured `BEARER_TOKEN` on first use — get a token from Meltano Cloud (e.g. `https://app.meltano.com/api-key`) and set it as the collection's `BEARER_TOKEN` variable to authenticate requests.

---

## Resource Index

Full documentation for each of these resources is in [`api-resources.md`](api-resources.md).

| Resource | One-line description |
|---|---|
| [Accounts](api-resources.md#accounts) | Passive entities storing quota/usage information (workspaces, rows, pipeline minutes, API clients) for profiles. |
| [Administrators](api-resources.md#administrators) | Members granted delegated workspace-owner-level management permissions. |
| [Alerts](api-resources.md#alerts) | User-created alerts on datasets used to surface dataset-related information. |
| [API Keys](api-resources.md#api-keys) | Client ID/secret credential pairs offering an alternate authentication method. |
| [Channels](api-resources.md#channels) | Groupings used to categorise datasets within a workspace. |
| [Comments](api-resources.md#comments) | Threaded conversation/collaboration on datasets. |
| [Datacomponents](api-resources.md#datacomponents) | Configured instances of a dataplugin (with settings/properties) used as building blocks for pipelines. |
| [Dataplugins](api-resources.md#dataplugins) | Definitions of data sources/destinations (taps/targets) and their configurable settings. |
| [Datasets](api-resources.md#datasets) | Chart.js-visualised data modules published to workspaces; support likes, views, comments, messages. |
| [Datastores](api-resources.md#datastores) | Destinations that pipelines load data into (default managed Postgres, or a custom loader). |
| [Deployments](api-resources.md#deployments) | Deploys a workspace's repository contents to Meltano Cloud, manually or via GitHub webhook. |
| [Feed](api-resources.md#feed) | The most relevant datasets for a user, ranked by interaction-derived score. |
| [Invitations](api-resources.md#invitations) | Email-based invitations granting access to private workspaces. |
| [Jobs](api-resources.md#jobs) | Stateful, trackable tasks (usually pipeline runs) with status, logs, and lifecycle. |
| [Members](api-resources.md#members) | Reduced-visibility view of a profile scoped to a particular workspace. |
| [News](api-resources.md#news) | Aggregated notification feed for a workspace, driven by subscriptions. |
| [Notifications](api-resources.md#notifications) | Alerts raised by resource events for subscribed users. |
| [Pipelines](api-resources.md#pipelines) | Configured sets of runnable actions (from datacomponents) executed as jobs, on schedule or on demand. |
| [Profiles](api-resources.md#profiles) | The individual user account/consumer of the Meltano Cloud service. |
| [Resources](api-resources.md#resources) | Arbitrary files managed within a workspace, addressable by path. |
| [Search](api-resources.md#search) | Dataset search within a workspace by free text, channel, tag, or elastic query. |
| [Subscriptions](api-resources.md#subscriptions) | Declared interest in a resource, controlling which notifications a user receives. |
| [Tags](api-resources.md#tags) | Hash-prefixed keywords extracted from dataset title/description/comments, used for search. |
| [Workspaces](api-resources.md#workspaces) | Isolated instances of the Meltano Cloud service scoping profiles, pipelines, datasets, etc. |

---

## Related Reference

- [DataML artifact reference](/reference/cloud/dataml/) is referenced throughout resource docs (ChannelML, DatasetML, DatastoreML, PipelineML, WorkspaceML) for the declarative YAML file formats that map onto these API resources.
