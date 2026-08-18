# Meltano Cloud API Resources

Detailed reference for every resource exposed by the Meltano Cloud REST API. See [`api-overview.md`](api-overview.md) for authentication, error format, HAL link conventions, pagination, and search/filter syntax that apply across all resources below.

Conventions used in this file:
- **Bold `METHOD` + path** marks each endpoint, e.g. **GET** `/api/workspaces`.
- Path parameters are written `{like-this}`.
- "HAL links" means the JSON response includes hypermedia links per the [Actions](api-overview.md#actions) conventions.
- Object field tables list the JSON shape as documented in source. Where a resource's endpoints don't include a worked request/response body in source (the docs site pulls these from a separate, generated example library not present in these markdown files), the field table is the authoritative shape reference instead.
- "Initialise" endpoints typically create a draft/stub resource (returning an `id`) that a subsequent `create`/`update` `PUT` to `.../{id}` finalises.

---

## Accounts

Accounts are passive entities that store quota information for resources consumed by associated [profiles](#profiles). An account is created for a user when they first sign up.

### Object: Account

| Path | JSON Type | Format | Description |
|---|---|---|---|
| `id` | `string` | Version 4 UUID | The account ID |
| `created` | `string` | ISO 8601 timestamp | The instant at which the account was created |
| `lastModified` | `string` | ISO 8601 timestamp | The instant at which the account was last modified |
| `company` | `string` | | The name of the company associated with the account |
| `ownerEmail` | `string` | Email address | The email address of the owner profile |
| `ownerProfileId` | `string` | | The ID of the owner profile |
| `maxWorkspaces` | `number` | Unsigned integer | The maximum number of workspaces that can be created under the account |
| `maxRows` | `number` | Unsigned integer | The maximum number of managed database rows available to the account |
| `minutesPerMonth` | `number` | Unsigned integer | The number of pipeline run minutes available to the account per month |
| `minutesUsed` | `number` | Unsigned integer | The number of pipeline run minutes used by the account per month |
| `maxClients` | `number` | Unsigned integer | The number of [API key](#api-keys) clients available to the account |

### Endpoints

**GET** `/api/accounts` — View all accounts.
Returns all accounts the authenticated user profile is an owner of. Response: `200 OK`, Account collection with HAL links.

**GET** `/api/accounts/{account-id}` — View an account.
Returns the account. Prerequisites: account must exist; authenticated profile must be an owner. Response: `200 OK`, Account with HAL links.

**POST** `/api/accounts/new` — Initialise a new account.
Response: `200 OK`, Account with HAL links.

**PUT** `/api/accounts/{account-id}` — Create an account.
Prerequisites: `ownerEmail` must match the authenticated user profile's email address. Body: Account resource. Response: `201 Created`, Account with HAL links.

**PUT** `/api/accounts/{account-id}` — Update an account.
Prerequisites: account must exist; authenticated profile must be an owner. Body: Account resource. Response: `200 OK`, Account with HAL links.

**GET** `/api/accounts/{account-id}/admins` — View all account admins.
Prerequisites: authenticated profile must be an owner. Response: `200 OK`, [Profile](#profiles) collection with HAL links.

**PUT** `/api/accounts/{account-id}/admins/{profile-id}` — Add an account admin.
Adds profile `{profile-id}` as an admin of the account. Prerequisites: authenticated profile must be an owner; profile `{profile-id}` must exist. Response: `200 OK`, Account with HAL links.

**DELETE** `/api/accounts/{account-id}/admins/{profile-id}` — Remove an account admin.
Prerequisites: authenticated profile must be an owner; profile `{profile-id}` must be an admin. Response: `204 No Content`.

**PUT** `/api/accounts/{account-id}/owner/{profile-id}` — Set an account owner.
Sets profile `{profile-id}` as the primary owner of the account. Prerequisites: authenticated profile must be an owner; profile `{profile-id}` must be an admin of the account. Response: `200 OK`, Account with HAL links.

**PUT** `/api/accounts/{account-id}/workspaces/{workspace-id}/transfer` — Transfer a workspace.
Transfers workspace `{workspace-id}` to account `{account-id}`. Prerequisites: user must be the owner of the account. Response: `200 OK`, [Workspace](#workspaces) with HAL links.

**See also:** [Set the working account for a profile](#profiles).

---

## Administrators

Administrators are types of [members](#members) with delegated [workspace](#workspaces) management permissions, equivalent to those held by the workspace owner.

### Object: Administrator

Extends [Member](#members).

| Path | JSON Type | Format | Description |
|---|---|---|---|
| `administrator` | `bool` | | Whether or not the member is an administrator |

### Endpoints

**GET** `/api/workspaces/{workspace-id}/administrators` — View all administrators of a workspace.
Prerequisites: user must be a member of the workspace. Response: `200 OK`, Administrator collection with HAL links.

**PUT** `/api/workspaces/{workspace-id}/administrators/{profile-id}` — Add an administrator to a workspace.
Adds profile `{profile-id}` as an administrator. Prerequisites: authenticated profile must be the workspace owner; profile `{profile-id}` must be a member of the workspace. Response: `200 OK`, Administrator with HAL links.

**DELETE** `/api/workspaces/{workspace-id}/administrators/{profile-id}` — Withdraw an administrator from a workspace.
Prerequisites: authenticated profile must be the workspace owner; profile `{profile-id}` must be an administrator. Response: `200 OK`, Administrator with HAL links.

---

## Alerts

Alerts can be created by users on [datasets](#datasets). These alerts can then be used to inform users of information related to that dataset.

### Endpoints

**POST** `/datasets/{dataset-id}/alerts` — Initialise an alert on a dataset.
Prerequisites: authenticated user must own a Meltano Cloud account. Response: `200 OK`.

**PUT** `/datasets/{dataset-id}/alerts/{alert-id}` — Create an alert on a dataset.
Prerequisites: authenticated user must own a Meltano Cloud account. Response: `201 Created`.

**GET** `/datasets/{dataset-id}/alerts` — View alerts on a dataset.
Prerequisites: authenticated user must own a Meltano Cloud account. Response: `200 OK`.

**GET** `/alerts/{alert-id}` — View an alert.
Prerequisites: authenticated user must own a Meltano Cloud account. Response: `200 OK`.

---

## API Keys

API keys offer an alternate method of authentication to the Meltano Cloud API using a client ID and secret.

### Object: API Key

| Path | JSON Type | Format | Description |
|---|---|---|---|
| `id` | `string` | Version 4 UUID | The API key ID |
| `created` | `string` | ISO 8601 timestamp | The instant when the API key was created |
| `lastModified` | `string` | ISO 8601 timestamp | The instant when the API key was last modified |
| `name` | `string` | | The API key name |
| `clientId` | `string` | | The API key client ID |
| `profileId` | `string` | | The API key owner profile ID |

### Endpoints

**GET** `/api/apikeys` — View all API keys.
Returns all API keys owned by the authenticated profile. Prerequisites: authenticated user must own a Meltano Cloud account; the API key must exist. Response: `200 OK`, API key collection with HAL links.

**GET** `/api/apikeys/{apikey-id}` — View an API key.
Prerequisites: as above. Response: `200 OK`, API key with HAL links.

**POST** `/api/apikeys` — Initialise an API key.
Prerequisites: authenticated user must own a Meltano Cloud account. Response: `200 OK`, API key with HAL links.

**PUT** `/api/apikeys/{apikey-id}` — Create an API key.
Prerequisites: authenticated user must own a Meltano Cloud account. Body: API key resource. Response: `201 Created`, API key with HAL links.

**PUT** `/api/apikeys/{apikey-id}` — Update an API key.
Prerequisites: authenticated user must own a Meltano Cloud account. Body: API key resource. Response: `200 OK`, API key with HAL links.

**DELETE** `/api/apikeys/{apikey-id}` — Delete an API key.
Prerequisites: authenticated user must own a Meltano Cloud account; API key must exist. Response: `204 No Content`.

---

## Channels

Channels enable datasets to be categorised or grouped together. A single workspace can have multiple channels.

### Object: Channel

| Path | JSON Type | Format | Description |
|---|---|---|---|
| `id` | `string` | Version 4 UUID | The channel ID |
| `creator` | `object` | [`Member`](#members) | The channel creator |
| `workspace` | `object` | [`Workspace`](#workspaces) | The channel workspace |
| `created` | `string` | ISO 8601 timestamp | The channel created-at timestamp |
| `lastModified` | `string` | ISO 8601 timestamp | The channel last-modified timestamp |
| `name` | `string` | | The channel name |
| `description` | `string` | | The channel description |
| `picture` | `string` | URL | The channel picture metadata |

### Endpoints

**POST** `/api/channels/{channel-id}` — Initialise a channel.
Response: `200 OK`, Channel with HAL links.

**GET** `/api/channels/{channel-id}` — View a channel.
Prerequisites: channel must exist. Response: `200 OK`, Channel with HAL links.

**GET** `/api/workspaces/{workspace-id}/channels/{channel-id}` — View a channel in a workspace.
Prerequisites: workspace must exist; user must be a member. Response: `200 OK`, Channel with HAL links.

**GET** `/api/workspaces/{workspace-id}/channels/{channel-id}?type={type}&source={source}&containsDataset={datasetId}` — View all channels in a workspace.
Prerequisites: workspace must exist; user must be a member.

Query parameters:

| Parameter | Required | Format | Default | Description |
|---|---|---|---|---|
| `type` | No | string | None | Return channels by type: `list` or `source` |
| `source` | No | string | None | Return channels by source: `profile` or `workspace` |
| `containsDataset` | No | string | None | Adds a `containsDataset` boolean field to all channels, indicating if it contains the dataset |

Response: `200 OK`, Channel collection with HAL links.

**PUT** `/api/workspaces/{workspace-id}/channels/{channel-id}` — Create or update a channel in a workspace.
Takes a `{channel-id}` UUID; based on the supplied value and existing channels in the workspace, updates or creates a channel accordingly. Prerequisites: workspace must exist; user must be an admin in the workspace. Response: `200 OK` / `201 Created`, Channel with HAL links.

**DELETE** `/api/channels/{channel-id}` — Delete a channel.
Prerequisites: user must be an admin of the workspace the channel is in. Response: `204 No Content`.

**GET** `/api/channels/{channel-id}` — View all channels in your workspace news.
Returns all channels in your news for the workspace. Response: `200 OK`, Channels in your workspace news.

**PUT** `/api/channels/{channel-id}/datasets/{dataset-id}` — Add a dataset to a list channel.
Adds a dataset to a channel with type list. Response: `201 Created`, no response body.

**DELETE** `/api/channels/{channel-id}/datasets/{dataset-id}` — Remove a dataset from a list channel.
Removes a dataset from a channel with type list. Response: `204 No Content`.

**PUT** `/api/channels/{channel-id}/scope/workspace` — Add workspace scope to a channel.
Response: `200 OK`, Channel with HAL links.

**PUT** `/api/channels/{channel-id}/scope/profile` — Withdraw workspace scope from a channel.
Response: `200 OK`, Channel with HAL links.

**See also:** [Subscribe to a channel](#subscriptions), [ChannelML](/reference/cloud/dataml/channelml/).

---

## Comments

Comments aid conversation and collaboration around workspace datasets. Comments can be made on datasets, or on other comments to form threads.

### Object: Comment

| Path | JSON Type | Format | Description |
|---|---|---|---|
| `id` | `string` | Version 4 UUID | The comment ID |
| `message` | `string` | | The comment message |
| `likeCount` | `number` | Unsigned integer | The number of likes the comment has received |
| `likedByProfiles` | `object[]` | Array of [`Member`](#members)s | The workspace members that have liked the comment |
| `created` | `string` | ISO 8601 timestamp | When the comment was created |
| `lastModified` | `string` | ISO 8601 timestamp | When the comment was last modified |
| `from` | `object` | [`Member`](#members) | The comment author |
| `commentCount` | `number` | Unsigned integer | The number of replies the comment has received |
| `datasetId` | `string` | Version 4 UUID | The ID of the dataset comment subject |
| `parentId` | `string` | Version 4 UUID | The ID of the parent comment |

### Endpoints

**GET** `/api/datasets/{dataset-id}/comments` — View all comments on a dataset.
Prerequisites: dataset must exist. Response: `200 OK`, Comment collection with HAL links.

**GET** `/api/comments/{comment-id}` — View a comment.
Prerequisites: comment must exist. Response: `200 OK`, Comment with HAL links.

**GET** `/api/comments/{comment-id}/history` — View the edit history of a comment.
Prerequisites: comment must exist. Response: `200 OK`.

**GET** `/api/comments/{comment-id}` — View all replies to a comment.
Prerequisites: comment must exist. Response: `200 OK`, Comment with HAL links.

**POST** `/api/datasets/{dataset-id}/comments` — Initialise a comment on a dataset.
Prerequisites: dataset must exist. Response: `200 OK`, Comment with HAL links.

**POST** `/api/comments/{comment-id}` — Initialise a reply to a comment.
Prerequisites: comment must exist. Response: `200 OK`, Comment with HAL links.

**PUT** `/api/comments/{comment-id}` — Create a comment.
Prerequisites: the comment must have been initialised in order to create it; the target dataset or comment must exist. Body: Comment resource. Response: `201 Created`, Comment with HAL links.

**PUT** `/api/comments/{comment-id}` — Update a comment.
Prerequisites: comment must exist. Body: Comment resource. Response: `200 OK`, Comment with HAL links.

**PUT** `/api/comments/{comment-id}/like` — Record a like of a comment.
Records a like from the authenticated profile. Prerequisites: comment must exist. Response: `200 OK`, no response body.

**DELETE** `/api/comments/{comment-id}/like` — Remove a like from a comment.
Prerequisites: comment must exist. Response: `204 No Content`.

**DELETE** `/api/comments/{comment-id}` — Delete a comment.
Prerequisites: comment must exist. Response: `204 No Content`.

---

## Datacomponents

Datacomponents hold configuration for [dataplugins](#dataplugins), and are the building blocks for constructing [pipelines](#pipelines). One dataplugin may be referenced by many datacomponents, each with a different set of `properties` for the dataplugin's [settings](#dataplugins). One pipeline may reference multiple datacomponents.

### Object: Datacomponent

| Path | JSON Type | Format | Description |
|---|---|---|---|
| `id` | `string` | Version 4 UUID | The datacomponent ID |
| `created` | `string` | ISO 8601 timestamp | When the datacomponent was created |
| `lastModified` | `string` | ISO 8601 timestamp | When the datacomponent was last modified |
| `name` | `string` | | The datacomponent name |
| `dataPlugin` | `string` | | Create/update with dataplugin `fullyQualifiedName` |
| `properties` | `object` | [`Properties`](#properties-datacomponent) | The datacomponent properties, defined by the dataplugin's [`settings`](#dataplugins). Properties are key-value pairs, where keys reference setting `name`s |

**Extractor Datacomponent** — datacomponents backed by dataplugins of `type: EXTRACTOR` additionally expose:

| Path | JSON Type | Format | Description |
|---|---|---|---|
| `streams` | `object[]` | Array of [Stream](#stream) | The available streams (populated after [verifying a pipeline](#pipelines) that references this datacomponent) |

#### Properties {#properties-datacomponent}

For each setting in the dataplugin's [`settings`](#dataplugins):

| Path | JSON Type | Format | Description |
|---|---|---|---|
| Refer to setting `name` | Refer to setting `kind` | Refer to setting `kind` | Refer to setting `description` |

**Reserved properties for extractor datacomponents:**

| Path | JSON Type | Format | Description |
|---|---|---|---|
| `_select` | `string` | JSON array | Meltano [stream and property selection rules](https://docs.meltano.com/concepts/plugins#select-extra) |
| `_metadata` | `string` | JSON object | Meltano [stream and property metadata rules](https://docs.meltano.com/concepts/plugins#metadata-extra) |

#### Stream

| Path | JSON Type | Format | Description |
|---|---|---|---|
| `name` | `string` | | The stream name |
| `selected` | `string` | [Entity Selection](#entity-selection) | The stream entity selection type |
| `fields` | `object[]` | Array of [Field](#field) | The available stream fields |

#### Field

| Path | JSON Type | Format | Description |
|---|---|---|---|
| `name` | `string` | | The field name |
| `selected` | `string` | [Entity Selection](#entity-selection) | The field entity selection type |

#### Format: Entity Selection {#entity-selection}

| Value | Description |
|---|---|
| `AUTOMATIC` | The entity is automatically selected by the underlying extractor and will always be synced |
| `SELECTED` | The entity is selected and will be synced |
| `EXCLUDED` | The entity is excluded and will not be synced |

### Endpoints

**GET** `/api/workspaces/{workspace-id}/datacomponents` — View all datacomponents in a workspace.
Prerequisites: workspace must exist. Response: `200 OK`, Datacomponent collection with HAL links.

**GET** `/api/datacomponents/{datacomponent-id}` — View a datacomponent.
Prerequisites: datacomponent must exist. Response: `200 OK`, Datacomponent with HAL links.

**POST** `/api/workspaces/{workspace-id}/datacomponents` — Initialise a new datacomponent in a workspace.
Response: `200 OK`, Datacomponent with HAL links.

**PUT** `/api/workspaces/{workspace-id}/datacomponents/{datacomponent-id}` — Create or update a datacomponent in a workspace.
Body: Datacomponent resource. Response: `200 OK` / `201 Created`, Datacomponent with HAL links.

**PUT** `/api/datacomponents/{datacomponent-id}` — Update a datacomponent.
Prerequisites: datacomponent must exist. Body: Datacomponent resource. Response: `200 OK`, Datacomponent with HAL links.

**DELETE** `/api/datacomponents/{datacomponent-id}` — Delete a datacomponent.
Response: `204 No Content`.

---

## Dataplugins

Dataplugins define a source of data from a given repository. Meltano Cloud provides pre-configured platform-wide dataplugins out of the box, as well as the ability to create custom dataplugins through the API. From these, [pipeline](#pipelines) jobs can be run to inject data into a workspace.

### Object: Dataplugin

| Path | JSON Type | Format | Description |
|---|---|---|---|
| `id` | `string` | Version 4 UUID | The dataplugin ID |
| `name` | `string` | | The dataplugin name |
| `description` | `string` | | A description of the dataplugin |
| `repositoryUrl` | `string` | URL | The dataplugin repository URL |
| `settings` | `object[]` | Array of [`Setting`](#setting) | The dataplugin settings |

#### Setting

| Path | JSON Type | Format | Description |
|---|---|---|---|
| `name` | `string` | | The setting name |
| `value` | `string` | | The setting default value |
| `label` | `string` | | The setting label |
| `protected` | `bool` | | The setting protection status |
| `kind` | `string` | [Setting Kind](#setting-kind) | The setting kind |
| `description` | `string` | | A description of the setting |
| `placeholder` | `string` | | The setting placeholder text |
| `envAliases` | `string[]` | | Environment variable aliases for the setting |
| `documentation` | `string` | URL | The setting documentation URL |
| `oauth` | [`OAuth`](#oauth) | | The setting OAuth configuration |
| `env` | `string` | | (undocumented further in source) |

#### OAuth

| Path | JSON Type | Format | Description |
|---|---|---|---|
| `provider` | `string` | | The OAuth provider |

#### Format: Setting Kind {#setting-kind}

`string` — one of:

| Value | Description |
|---|---|
| `STRING` | String setting |
| `INTEGER` | Integer setting |
| `PASSWORD` | Password setting |
| `HIDDEN` | Hidden setting |
| `BOOLEAN` | Boolean setting |
| `DATE_ISO8601` | ISO 8601 date setting |
| `EMAIL` | Email setting |
| `OAUTH` | OAuth setting |
| `FILE` | File setting |
| `ARRAY` | Array setting |

### Endpoints

**GET** `/api/dataplugins` — View all supported dataplugins.
Returns all dataplugins supported by Meltano Cloud. Response: `200 OK`, Dataplugin collection with HAL links.

**GET** `/api/workspaces/{workspace-id}/dataplugins` — View all workspace dataplugins.
Returns all dataplugins available to the workspace. Prerequisites: workspace must exist. Response: `200 OK`, Dataplugin collection with HAL links.

**GET** `/api/dataplugins/{dataplugin-id}` — View a dataplugin.
Prerequisites: dataplugin must exist. Response: `200 OK`, Dataplugin with HAL links.

**POST** `/api/dataplugins` — Initialise a new dataplugin.
Response: `200 OK`, Dataplugin with HAL links.

**PUT** `/api/dataplugins/{dataplugin-id}` — Create a dataplugin.
Body: Dataplugin resource. Response: `201 Created`, Dataplugin with HAL links.

**PUT** `/api/dataplugins/{dataplugin-id}` — Update a dataplugin.
Prerequisites: dataplugin must exist. Body: Dataplugin resource — fields that may be updated: `description` (string), `repositoryUrl` (string, URL to the dataplugin repository), `settings` (array of Setting). Response: `200 OK`, Dataplugin with HAL links.

**DELETE** `/api/dataplugins/{dataplugin-id}` — Delete a dataplugin.
Response: `204 No Content`.

---

## Datasets

Datasets are modules of data that can be published to workspaces. Datasets are visualised in Meltano Cloud following the [Chart.js](https://www.chartjs.org/) specifications.

### Object: Dataset

| Path | JSON Type | Format | Description |
|---|---|---|---|
| `id` | `string` | Version 4 UUID | The dataset ID |
| `published` | `string` | ISO 8601 timestamp | The instant the dataset was published |
| `alias` | `string` | | The dataset alias |
| `workspaceId` | `string` | Version 4 UUID | The workspace ID of the published dataset |
| `source` | `string` | | The channel ID where the dataset was initially published to |
| `title` | `string` | | The dataset title |
| `description` | `string` | | The dataset description (may contain markdown) |
| `questions` | `string` | | The dataset questions |
| `rawData` | `string` | JSON | The dataset raw data |
| `visualisation` | `string` | JSON | The dataset visualisation metadata. See DatasetML visualisation docs. |
| `metadata` | `string` | JSON | The dataset metadata. See DatasetML metadata docs. |
| `query` | `string` | SQL statement | The dataset query. See DatasetML query docs. |
| `likeCount` | `number` | Unsigned integer | The number of likes the dataset has received |
| `likedByProfiles` | `object[]` | Array of [`Member`](#members) | The members that have liked the dataset |
| `commentCount` | `number` | Unsigned integer | The number of comments the dataset has received |
| `viewCount` | `number` | Unsigned integer | The number of views the dataset has received |
| `created` | `string` | ISO 8601 timestamp | The instant the dataset was created |
| `score` | `number` | Decimal | The dataset score used to determine its position in the workspace [Feed](#feed) |

### Object: Dataset Message

| Path | JSON Type | Format | Description |
|---|---|---|---|
| `id` | `string` | Version 4 UUID | The dataset message ID (shared with the resulting [notification](#notifications)) |
| `recipientId` | `string` | | The recipient profile ID |
| `message` | `string` | | The dataset message content |
| `datasetId` | `string` | Version 4 UUID | The message subject dataset ID |

### Endpoints

**GET** `/api/workspaces/{workspace-id}/datasets` — View all datasets in a workspace.
Prerequisites: user must be a member of the workspace. Response: `200 OK`, Dataset collection with HAL links.

**GET** `/api/workspaces/{workspace-id}/liked` — View all liked datasets in a workspace.
Returns all datasets liked by the authenticated profile. Prerequisites: user must be a member of the workspace. Response: `200 OK`, Dataset collection with HAL links.

**GET** `/api/channels/{channel-id}/datasets` — View datasets by channel.
Prerequisites: channel must exist. Response: `200 OK`, Dataset collection with HAL links.

**GET** `/api/datasets/{dataset-id}` — View a dataset.
Prerequisites: dataset must exist. Response: `200 OK`, Dataset with HAL links.

**GET** `/api/workspaces/{workspace-id}/datasets/{dataset-id-or-alias}` — View a dataset in a workspace.
Prerequisites: user must be a member of the workspace; dataset must exist within the workspace. Response: `200 OK`, Dataset with HAL links.

**GET** `/api/datasets/{dataset-id}/data` — View the data of a dataset.
Prerequisites: dataset must exist.

Headers — `Accept`:

| Media Type(s) | Description |
|---|---|
| `application/json`, `*/*` | JSON response (default, given `*/*` or no `Accept` header) |
| `text/csv` | CSV response |

Response: `200` — the dataset data (defaults to JSON); `204` — no response body.

**POST** `/api/workspaces/{workspace-id}/datasets` — Publish a dataset to a workspace.
Prerequisites: user must be a member of the workspace. Making the request with an existing `id` or `alias` overwrites the respective dataset. Body: Dataset resource. Response: `200 OK` / `201 Created`, Dataset with HAL links.

**PATCH** `/api/datasets/{dataset-id}` — Edit a dataset.
Prerequisites: dataset must exist. This request can update one or more Dataset fields at once — e.g. `title` only, or both `title` and `description` together. Response: `200 OK`, Dataset with HAL links.

**PUT** `/api/datasets/{dataset-id}/view` — Record a view of a dataset.
Adds a view to the dataset. Prerequisites: dataset must exist. Response: `200 OK`, no response body.

**PUT** `/api/datasets/{dataset-id}/like` — Record a like of a dataset.
Records a like from the authenticated profile. Prerequisites: dataset must exist. Response: `200 OK`, no response body.

**DELETE** `/api/datasets/{dataset-id}/like` — Remove a like from a dataset.
Prerequisites: dataset must exist. Response: `204 No Content`.

**POST** `/api/datasets/{dataset-id}/messages` — Initialise a new dataset message.
Prerequisites: dataset must exist. Response: `200 OK`, Dataset Message with HAL links.

**PUT** `/api/datasets/{dataset-id}/messages/{message-id}` — Create or update a dataset message.
Creates or updates the dataset message; this appears as a `DATASET_MESSAGE` [notification](#notifications) type for the recipient. Prerequisites: dataset must exist. Body: Dataset Message resource. Response: `200 OK` / `201 Created`, Dataset Message with HAL links.

**DELETE** `/api/datasets/{dataset-id}` — Delete a dataset.
Prerequisites: dataset must exist. Response: `204 No Content`.

Further reading: [Meltano Cloud DatasetML YAML file](/reference/cloud/dataml/datasetml/), [Example Charts](/reference/cloud/dataml/datasetml/basic-examples).

**See also:** [View all comments on a dataset](#comments), [Search for datasets by free text/channel/tag](#search), [Subscribe to a dataset](#subscriptions).

---

## Datastores

Datastores define a destination for data loaded into a [workspace](#workspaces) by [pipelines](#pipelines). The default datastore for a workspace is its own PostgreSQL database hosted by Meltano Cloud, but this can be changed at any time to another datastore with your own credentials (see supported [dataplugins](#dataplugins) of type `LOADER`).

### Object: Datastore

| Path | JSON Type | Format | Description |
|---|---|---|---|
| `id` | `string` | Version 4 UUID | The datastore ID |
| `created` | `string` | ISO 8601 timestamp | The instant at which the datastore was created |
| `lastModified` | `string` | ISO 8601 timestamp | The instant at which the datastore was last modified |
| `name` | `string` | | The datastore name |
| `dataPlugin` | `string` | | Create/update with dataplugin `fullyQualifiedName` |
| `workspace` | `string` | Version 4 UUID | The datastore's workspace `id` |
| `jdbcUrl` | `string` | [JDBC URL](https://docs.oracle.com/javase/tutorial/jdbc/basics/connecting.html) | The datastore JDBC URL |
| `properties` | `object` | [`Properties`](#properties-datastore) | The datastore properties |

#### Properties {#properties-datastore}

For each setting `s` in the dataplugin's [`settings`](#dataplugins):

| Path | Type | Description |
|---|---|---|
| `s.name` | `s.kind` | Refer to `s.description` |

### Endpoints

**GET** `/api/workspaces/{workspace-id}/datastores` — View all datastores in a workspace.
Prerequisites: workspace must exist. Response: `200 OK`, Datastore collection with HAL links.

**GET** `/api/datastores/{datastore-id}` — View a datastore.
Prerequisites: datastore must exist. Response: `200 OK`, Datastore with HAL links.

**PUT** `/api/datastores/{datastore-id}/default` — Set a datastore as the workspace default.
Prerequisites: datastore must exist. Response: `200 OK`, no response body.

**POST** `/api/workspaces/{workspace-id}/datastores` — Initialise a new datastore in a workspace.
Prerequisites: workspace must exist. Response: `200 OK`, Datastore with HAL links.

**PUT** `/api/workspaces/{workspace-id}/datastores/{datastore-id}` — Create or update a datastore in a workspace.
Prerequisites: workspace must exist. Body: Datastore resource. Response: `200 OK` / `201 Created`, Datastore with HAL links.

**DELETE** `/api/datastores/{datastore-id}` — Delete a datastore.
Prerequisites: datastore must exist. Response: `204 No Content`.

**See also:** [DatastoreML](/reference/cloud/dataml/datastoreml/).

---

## Deployments

Deployments let the user schedule a [job](#jobs) to deploy the contents of their [workspace](#workspaces) repository to their workspace in Meltano Cloud.

This can be done manually or via a [GitHub repository webhook](https://docs.github.com/en/webhooks/using-webhooks/creating-webhooks#creating-a-repository-webhook):
- Payload URL: `https://app.meltano.com/api/workspaces/<workspace_id>/deployments/github-webhook`
- Content type: `application/json`
- Secret: the "Deployment Secret" from workspace settings in Meltano Cloud

### Endpoints

**POST** `/api/workspaces/{workspace-id}/deployments` — Deploy your workspace repository.
Response: `202 Accepted`, [Job](#jobs) with HAL links.

**POST** `/api/workspaces/{workspace-id}/deployments/github-webhook` — GitHub webhook workspace deployment.
Receives `POST` requests from GitHub and starts a workspace deploy job. Response: `202 Accepted`, [Job](#jobs) with HAL links.

---

## Feed

The feed returns the most relevant datasets for the authenticated user profile. [Member](#members) interactions with datasets are scored, determining their position within the feed.

User and member interactions that affect a dataset's score:
- Creating or modifying a dataset
- Viewing a dataset
- Liking a dataset
- Commenting on a dataset

### Endpoints

**GET** `/api/workspaces/{workspace-id}/feed` — View the feed of a workspace.
Prerequisites: workspace must exist. Response: `200 OK`, [Dataset](#datasets) collection with HAL links.

**See also:** [View all datasets in a workspace](#datasets).

---

## Invitations

Invitations allow access to private workspaces. When an invitation is created, an email containing an access link to the workspace is sent to the recipient. Invitations can be sent to email addresses under the allowed domains configured for a workspace.

### Object: Invitation

| Path | JSON Type | Format | Description |
|---|---|---|---|
| `id` | `string` | Version 4 UUID | The invitation ID |
| `created` | `string` | ISO 8601 timestamp | The instant the invitation was created |
| `lastModified` | `string` | ISO 8601 timestamp | The instant the invitation was last modified |
| `status` | `string` | [Invitation Status](#invitation-status) | The invitation status |
| `email` | `string` | Email address | The invitation target email address |
| `creator` | `object` | [`Member`](#members) | The invitation creator |
| `workspace` | `object` | [`Workspace`](#workspaces) | The invitation target workspace |

#### Format: Invitation Status {#invitation-status}

`string` — one of:

| Value | Description |
|---|---|
| `ACCEPTED` | The invitation has been accepted by the recipient |
| `PENDING` | The invitation has been sent to the recipient and is awaiting acceptance |
| `REVOKED` | The invitation has been revoked and can no longer be accepted |

### Endpoints

**GET** `/api/invitations` — View all sent invitations.
Returns all invitations sent by the authenticated profile. Response: `200 OK`, Invitation collection with HAL links.

**GET** `/api/invitations?email={user-email}` — View all received invitations.
Returns all invitations received by the authenticated profile. Response: `200 OK`, Invitation collection with HAL links.

**GET** `/api/workspaces/{workspace-id}/invitations` — View all invitations to a workspace.
As a workspace owner: returns all active invitations to the workspace. As a workspace member: returns all active invitations sent by the authenticated profile. Prerequisites: user must be a member of the workspace. Response: `200 OK`, Invitation collection with HAL links.

**POST** `/api/workspaces/{workspace-id}/invitations` — Create an invitation to a workspace.
Prerequisites: user must be a member of the workspace. Body: Invitation resource. Response: `202 Accepted`, no response body.

**PATCH** `/api/invitations/{invitation-id}` — Accept an invitation.
Prerequisites: workspace must exist; invitation must exist for the authenticated profile. Response: `200 OK`, Invitation with HAL links.

**DELETE** `/api/invitations/{invitation-id}` — Delete an invitation.
Deletes a pending or revoked invitation. Prerequisites: authenticated user must be the owner of the workspace the invitation belongs to, or must have sent the invitation. Response: `204 No Content`.

**PUT** `/api/invitations/{invitation-id}/revoked` — Withdraw an invitation.
Withdraws a pending or accepted invitation. Prerequisites: authenticated user must be the owner of the workspace the invitation belongs to, or must have sent the invitation. Response: `200 OK`, no response body.

---

## Jobs

A job is an arbitrary task with some stored state, pertaining to the governing [workspace](#workspaces). Typically, jobs are orchestrated by [pipeline](#pipelines) operations, but can also represent tasks for the user to complete.

### Object: Job

| Path | JSON Type | Format | Description |
|---|---|---|---|
| `id` | `string` | Version 4 UUID | The job ID |
| `created` | `string` | ISO 8601 timestamp | The instant at which the job was created |
| `type` | `string` | [Job Type](#job-type) | The descriptor for the process undertaken by the job |
| `exitCode` | `number` | Process exit status | The job exit code |
| `status` | `string` | [Job Status](#job-status) | The job status |
| `startTime` | `string` | ISO 8601 timestamp | The instant at which the job run started |
| `endTime` | `string` | ISO 8601 timestamp | The instant at which the job run ended |

#### Format: Job Status {#job-status}

`string` — one of:

| Value | Description |
|---|---|
| `QUEUED` | The job is queued |
| `RUNNING` | The job is running |
| `COMPLETE` | The job finished with no errors |
| `ERROR` | The job finished with errors |
| `STOPPED` | The job timed out or was manually stopped |

#### Format: Job Type {#job-type}

`string` — one of:

| Value | Description |
|---|---|
| `WORKSPACE_INIT` | System task to create a Meltano project in a workspace repository — automatically run when a workspace is created |
| `PIPELINE_CONFIG` | System task to configure the Meltano project and publish datasets with reference to a pipeline — automatically run when a pipeline is created, or a pipeline with status `FAILED` is updated |
| `PIPELINE_VERIFY` | System task to display and test the configuration of a pipeline |
| `PIPELINE_RUN` | System task to run a pipeline to load data into the workspace's default datastore, or some other external destination — manually run by the user or automatically run on the defined `schedule` |
| `PROFILE_COLLABORATE` | User task to send an invitation |
| `PROFILE_IMPORT` | User task to create a pipeline |

### Endpoints

**GET** `/api/workspaces/{workspace-id}/jobs` — View all running or completed jobs for a workspace.
Prerequisites: workspace must exist. Response: `200 OK`, Job collection with HAL links.

**GET** `/api/pipelines/{pipeline-id}/jobs` — View all running or completed jobs for a pipeline.
Prerequisites: pipeline must exist. Response: `200 OK`, Job collection with HAL links.

**GET** `/api/jobs/{job-id}` — View a job.
Prerequisites: job must exist. Response: `200 OK`, Job with HAL links.

**GET** `/api/jobs/{job-id}/logs?sequence={sequence}` — View the logs of a job.
Prerequisites: job must exist.

Query parameters:

| Parameter | Format | Default | Description |
|---|---|---|---|
| `sequence` | Unsigned integer | `0` | The line number in the logs to read from |

Headers — `Accept`:

| Media Type(s) | Description |
|---|---|
| `text/plain`, `*/*` | Plain text response |
| `application/stream+json`, `application/x-ndjson` | [NDJSON](http://ndjson.org/) response |

Response: `200` — job logs in the format specified by `Accept`; `204` — no response body.

**POST** `/api/pipelines/{pipeline-id}/jobs` — Create a job from a pipeline.
Prerequisites: pipeline must exist and not already be running. Response: `201 Created`, Job with HAL links.

**PUT** `/api/jobs/{job-id}/stopped` — Stop a job.
Prerequisites: job must exist; job must have status `RUNNING`. Response: `202 Accepted`, job stop acceptance message.

**DELETE** `/api/jobs/{job-id}` — Delete a job.
Deletes and stops the execution of the job. Prerequisites: job must exist. Response: `204 No Content`.

---

## Members

Members are users that belong to a particular [workspace](#workspaces). Every member is derived from a corresponding [profile](#profiles), inheriting its `id` and `name`. Within the scope of a workspace, each member is visible to one another, so operating with a reduced property set enhances data security.

### Object: Member

| Path | JSON Type | Format | Description |
|---|---|---|---|
| `id` | `string` | Version 4 UUID | The member ID (derived from corresponding profile ID) |
| `name` | `string` | | The member name (derived from corresponding profile name) |
| `handle` | `string` | | The unique `@`-prefixed handle for this member (derived from corresponding profile handle) |

### Endpoints

**GET** `/api/workspaces/{workspace-id}/members` — View all members of a workspace.
Prerequisites: user must be a member of the workspace. Response: `200 OK`, Member collection with HAL links.

**GET** `/api/workspaces/{workspace-id}/members/{member-id}` — View a member of a workspace.
Prerequisites: user must be a member of the workspace. Response: `200 OK`, Member with HAL links.

---

## News

News is a collection of [notifications](#notifications) resulting from all configured [subscriptions](#subscriptions). News is used to form a feed of [datasets](#datasets) specific to the authenticated user profile, in the context of a [workspace](#workspaces).

### Endpoints

**GET** `/api/workspaces/{workspace-id}/news?before={before}&since={since}` — View the news for a workspace.
Unlike [View all notifications](#notifications), this returns all notifications triggered by subscriptions configured for both the workspace and the authenticated user profile.

Query parameters:

| Parameter | Required | Format | Default | Description |
|---|---|---|---|---|
| `before` | No | ISO 8601 timestamp | The instant the request was made | Return notifications created before this instant |
| `since` | No | ISO 8601 timestamp | `2021-02-11T11:12` | Return notifications created since this instant |
| `q` | No | Tag [filter](api-overview.md#searching-and-filtering) | | Tag(s) to search notifications by |

Response: `200 OK`, [Notification](#notifications) collection with HAL links.

**See also:** [View all tags in the news for a workspace](#tags).

---

## Notifications

Notifications are alerts triggered by certain events pertaining to a resource. To receive notifications for a specific resource, a user must have a [subscription](#subscriptions) to the resource.

### Object: Notification

| Path | JSON Type | Format | Description |
|---|---|---|---|
| `id` | `string` | Version 4 UUID | The notification ID |
| `created` | `string` | ISO 8601 timestamp | The instant the notification was created |
| `lastModified` | `string` | ISO 8601 timestamp | The instant the notification was last modified |
| `actor` | `object` | [`Member`](#members) | The member whose action raised this notification |
| `type` | `string` | [Notification Type](#notification-type) | The type of notification |
| `resolved` | `bool` | | Whether or not the notification has been read |

#### Format: Notification Type {#notification-type}

`string` — one of:

| Value | Description |
|---|---|
| `DATASET_ACTIVITY` | Any activity on the dataset |
| `DATASET_ANOMALY` | A detected anomaly in the dataset data |
| `DATASET_COMMENT` | A comment on the dataset |
| `DATASET_LIKE` | A like recorded on the dataset |
| `DATASET_MESSAGE` | A message about the dataset |
| `JOB_STARTED` | A job started for a pipeline |
| `JOB_ENDED` | A job ended for a pipeline |

### Endpoints

**GET** `/api/notifications?all={all}&before={before}&since={since}` — View all notifications.
Returns all notifications for the authenticated profile.

Query parameters:

| Parameter | Required | Format | Default | Description |
|---|---|---|---|---|
| `all` | No | Boolean | `false` | Whether to return both resolved and unresolved notifications |
| `before` | No | ISO 8601 timestamp | The instant the request was made | Return notifications created before this instant |
| `since` | No | ISO 8601 timestamp | `2021-02-11T11:12` | Return notifications created since this instant |

Response: `200 OK`, Notification collection with HAL links.

**GET** `/api/workspaces/{workspaceId}/notifications?all={all}&before={before}&since={since}` — View all notifications for a workspace.
Prerequisites: workspace must exist.

Query parameters: same as above (`all`, `before`, `since`).

Response: `200 OK`, Notification collection with HAL links.

**GET** `/api/notifications/{notification-id}` — View a notification.
Prerequisites: notification must exist. Response: `200 OK`, Notification with HAL links.

**PUT** `/api/notifications?since={since}&markAsResolved={markAsResolved}` — Refresh notifications.
Returns new notifications for the authenticated profile, optionally marking existing notifications as resolved up to the request instant or the supplied `since`.

Query parameters:

| Parameter | Required | Format | Default | Description |
|---|---|---|---|---|
| `since` | No | ISO 8601 timestamp | The instant the request was made | Fetch new notifications from this instant |
| `markAsResolved` | No | Boolean | `true` | Whether to mark notifications created up to `since` as resolved |

Response: `200 OK`, Notification collection with HAL links.

**DELETE** `/api/notifications/{notification-id}` — Delete a notification.
Prerequisites: notification must exist. Response: `204 No Content`.

**See also:** [Create or update a dataset message](#datasets).

---

## Pipelines

A pipeline defines a set of runnable actions composed from [datacomponents](#datacomponents) to complete a set of tasks — for example, [ELT](https://en.wikipedia.org/wiki/Extract,_load,_transform). Pipelines are run as [jobs](#jobs), either manually or on a predetermined schedule. Only a single pipeline can be run at any given time.

### Object: Pipeline

| Path | JSON Type | Format | Description |
|---|---|---|---|
| `id` | `string` | Version 4 UUID | The pipeline ID |
| `status` | `string` | [Pipeline Status](#pipeline-status) | |
| `name` | `string` | | The pipeline name |
| `schedule` | `string` | Cron | The interval at which to launch a new job, e.g. `0 0 9-17 * * MON-FRI` launches a job on the hour nine-to-five weekdays |
| `timeout` | `number` | Unsigned integer | Seconds after which the job will terminate — if `0`, an implicit default of 300 seconds is used |
| `maxRetries` | `number` | Unsigned integer | Maximum retries to attempt for a job ending with `ERROR` |
| `script` | `string` | Bash script | Custom script to execute during a job |
| `created` | `string` | ISO 8601 timestamp | When the pipeline was created |
| `lastModified` | `string` | ISO 8601 timestamp | When the pipeline was last modified |
| `properties` | `object` | [`Properties`](#properties-pipeline) | The pipeline properties, defined by the dataplugin `settings` of each datacomponent. Keys reference setting `name`s qualified by datacomponent `name`s |
| `dataComponents` | `string[]` | Array of datacomponent `name`s | The pipeline's datacomponent names, or create/update with dataplugin `fullyQualifiedName` |
| `actions` | `string[]` | Array of datacomponent `name`s or commands | The pipeline actions to run during a job |
| `triggeredBy` | `string[]` | Array of pipeline `name`s or workspace task identifiers | Pipelines or workspace tasks that trigger this pipeline on successful completion. Supported workspace task value (case-insensitive): `deploy` — workspace [deployment](#deployments) |

#### Properties {#properties-pipeline}

For each setting in the datacomponents' dataplugin [`settings`](#dataplugins):

| Path | JSON Type | Format | Description |
|---|---|---|---|
| `{datacomponent_name}.{setting_name}` | Refer to setting `kind` | Refer to setting `kind` | Refer to setting `description` |

- Any required settings not satisfied by a datacomponent property must be provided as a pipeline property.
- Any settings already satisfied by a datacomponent property can be overridden by a pipeline property.

**Reserved properties for extractor datacomponents:**

| Path | JSON Type | Format | Description |
|---|---|---|---|
| `{datacomponent_name}._select` | `string` | JSON array | Meltano [stream and property selection rules](https://docs.meltano.com/concepts/plugins#select-extra) |
| `{datacomponent_name}._metadata` | `string` | JSON object | Meltano [stream and property metadata rules](https://docs.meltano.com/concepts/plugins#metadata-extra) |

#### Format: Pipeline Status {#pipeline-status}

| Value | Description |
|---|---|
| `READY` | The pipeline completed processing resource changes |
| `PROVISIONING` | The pipeline is processing resource changes |
| `FAILED` | The pipeline failed to process resource changes |

### Endpoints

**GET** `/api/workspaces/{workspace-id}/pipelines` — View all pipelines in a workspace.
Returns all configured pipelines in the workspace. Prerequisites: workspace must exist. Response: `200 OK`, Pipeline collection with HAL links.

**GET** `/api/pipelines/{pipeline-id}` — View a pipeline.
Prerequisites: pipeline must exist. Response: `200 OK`, Pipeline with HAL links.

**POST** `/api/workspaces/{workspace-id}/pipelines` — Initialise a pipeline in a workspace.
Prerequisites: workspace must exist. Response: `200 OK`, Pipeline with HAL links.

**PUT** `/api/workspaces/{workspace-id}/pipelines/{pipeline-id}` — Create or update a pipeline in a workspace.
Prerequisites: workspace must exist. Body: Pipeline resource. Response: `200 OK` / `201 Created`, Pipeline with HAL links.

**PUT** `/api/workspaces/{workspace-id}/pipelines/{pipeline-id}/draft` — Create or update a pipeline as a draft.
Prerequisites: workspace must exist. Body: Pipeline resource. Response: `200 OK` / `201 Created`, Pipeline with HAL links.

**POST** `/api/workspaces/{workspace-id}/pipelines/validation` — Validate a pipeline configuration in a workspace.
Prerequisites: workspace must exist. Body: Pipeline resource. Response: `200 OK` — no response body; `400 Bad Request` — [Pipeline property](#properties-pipeline) validation errors.

**POST** `/api/pipelines/{pipeline-id}/verification` — Verify a pipeline.
Verifies the configuration of the pipeline. Prerequisites: pipeline must exist. Response: `200 OK`, [Job](#jobs) with HAL links.

**DELETE** `/api/pipelines/{pipeline-id}` — Delete a pipeline.
Prerequisites: pipeline must exist. Response: `204 No Content`.

**GET** `/api/pipelines/{pipeline-id}/metrics` — View pipeline metrics.
Returns pipeline metrics for each job of the pipeline. Prerequisites: pipeline must exist. Response: `200` — the metrics data (defaults to JSON format); `204` — no response body, metrics not enabled.

**See also:** [View all running or completed jobs for a pipeline](#jobs), [Create a job from a pipeline](#jobs), [Subscribe to a pipeline](#subscriptions), [PipelineML](/reference/cloud/dataml/pipelineml/).

---

## Profiles

Profiles are individual consumers of the Meltano Cloud service. A profile is automatically created for a user when they first access the app, or accept an invitation to a workspace from an existing member via email.

### Object: Profile

| Path | JSON Type | Format | Description |
|---|---|---|---|
| `id` | `string` | Version 4 UUID | The profile ID |
| `name` | `string` | | The full name of the person or entity represented by this profile |
| `handle` | `string` | | The unique `@`-prefixed handle for this profile (generated and read-only) |
| `phone` | `string` | Phone number | The profile phone number |
| `email` | `string` | Email address | The profile email address |
| `defaultWorkspace` | `object` | [`Workspace`](#workspaces) | The profile default workspace |
| `workingAccount` | `object` | [`Account`](#accounts) | The profile working account under which new workspaces are created |

### Endpoints

**GET** `/api/profiles` — View all profiles.
Returns all profiles under the authenticated user account. Response: `200 OK`, Profile collection with HAL links.

**GET** `/api/profiles/{profile-id}` — View a profile.
Prerequisites: profile must exist under the authenticated user account. Response: `200 OK`, Profile with HAL links.

**PUT** `/api/profiles/{profile-id}` — Create or update profile.
Prerequisites: the authentication subject must match the profile ID. Body: Profile resource. Response: `200 OK` / `201 Created`, Profile with HAL links.

**PATCH** `/api/profiles/{profile-id}` — Set a workspace as default.
Prerequisites: the authentication subject must match the profile ID. A workspace can be set as default, defining the environment Meltano Cloud initially loads for a given profile; this setting persists only for the profile that sets it. Body: Profile resource. Response: `200 OK`, Profile with HAL links.

**PUT** `/api/profiles/{profile-id}/working-account/{account-id}` — Set the working account for a profile.
Prerequisites: profile must exist; account must exist; authentication subject must match the profile ID; the profile must be an owner of the account. Response: `200 OK`, Profile with HAL links.

**See also:** [View all account admins](#accounts), [Add an account admin](#accounts), [Remove an account admin](#accounts), [Set an account owner](#accounts).

---

## Resources

Resources are files that are managed by a workspace. A resource is accessible from `/api/workspaces/{workspace-id}/resources` by its `path`.

### Object: Resource

| Path | JSON Type | Format | Description |
|---|---|---|---|
| `path` | `string` | | The resource path |
| `created` | `string` | ISO 8601 timestamp | The instant the resource was created |
| `lastModified` | `string` | ISO 8601 timestamp | The instant the resource was last modified |
| `contentType` | `string` | [MIME type](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types) | The content type of the resource |
| `content` | `string` | | The content of the resource |

### Endpoints

**GET** `/api/workspaces/{workspace-id}/resources/{resource-path}` — View a resource in a workspace.
Prerequisites: workspace must exist; resource must exist. Response: `200 OK`, Resource with HAL links.

**GET** `/api/workspaces/{workspace-id}/resources/{resource-path}` — View the content of a resource in a workspace.
Prerequisites: workspace must exist; resource must exist. Response: `200 OK`, the resource content.

**GET** `/api/workspaces/{workspace-id}/resources` — View all resources in a workspace.
Prerequisites: workspace must exist; resource must exist. Response: `200 OK`, Resource collection with HAL links.

**POST** `/api/workspaces/{workspace-id}/resources` — Publish multiple resources to a workspace.
Prerequisites: workspace must exist. Response: `200 OK`, Resource collection with HAL links.

**PUT** `/api/workspaces/{workspace-id}/resources/{resource-path}` — Create or update a resource in a workspace.
Prerequisites: workspace must exist. Body: Resource resource. Response: `200 OK` / `201 Created`, Resource with HAL links.

**DELETE** `/api/workspaces/{workspace-id}/resources/{resource-path}` — Delete a resource in a workspace.
Prerequisites: workspace must exist. Response: `204 No Content`.

---

## Search

[Datasets](#datasets) can be searched for within their containing [workspace](#workspaces). Searches can filter datasets by arbitrary text, [channel](#channels) name, or [tag](#tags) name. See [Searching and Filtering](api-overview.md#searching-and-filtering) for query construction details.

### Endpoints

**GET** `/api/workspaces/{workspaces-id}/search?q={free-text}` — Search for datasets in a workspace by free text.
Prerequisites: workspace must exist. Response: `200 OK`; `204 No Content` — no response body.

**GET** `/api/workspaces/{workspaces-id}/search?q=in:{channel-name}` — Search for datasets in a workspace by channel name.
Prerequisites: workspace must exist. Response: `200 OK`, [Dataset](#datasets) collection with HAL links; `204 No Content` — no response body.

**GET** `/api/workspaces/{workspace-id}/search?q=tag:{tag-name}` — Search for datasets in a workspace by tag name.
Prerequisites: workspace must exist. Response: `200 OK`; `204 No Content` — no response body.

**POST** `/api/workspaces/{workspace-id}/datasets/_msearch` — Search for datasets in a workspace using msearch.
Searches the workspace for datasets using an elastic search query. Prerequisites: workspace must exist. Response: `200 OK`; `204 No Content` — no response body.

---

## Subscriptions

Subscriptions are a declaration of interest in a particular resource, allowing a user to receive [notifications](#notifications) when certain events occur. The events that trigger notifications are controlled by the [type of subscription](#subscription-type).

### Object: Subscription

| Path | JSON Type | Format | Description |
|---|---|---|---|
| `id` | `string` | Version 4 UUID | The subscription ID |
| `created` | `string` | ISO 8601 timestamp | The instant the subscription was created |
| `lastModified` | `string` | ISO 8601 timestamp | The instant the subscription was last modified |
| `type` | `string` | [Subscription Type](#subscription-type) | The type of subscription |

#### Format: Subscription Type {#subscription-type}

`string` — one of:

| Value | Description |
|---|---|
| `ALL` | Triggers notifications for all resource events |
| `ALERTS` | Triggers notifications for resource alert events only |
| `NONE` | Does not trigger any notifications |

### Endpoints

**GET** `/api/subscriptions` — View all subscriptions.
Returns all subscriptions for the authenticated profile. Response: `200 OK`, Subscription collection with HAL links.

**GET** `/api/workspaces/{workspace-id}/members/subscriptions` — View all member subscriptions to a workspace.
Prerequisites: workspace must exist. Response: `200 OK`, Subscription collection with HAL links.

**GET** `/api/subscriptions/{subscription-id}` — View a subscription.
Prerequisites: subscription must exist. Response: `200 OK`, Subscription with HAL links.

**POST** `/api/workspaces/{workspace-id}/subscriptions` — Subscribe to a workspace.
Subscribes the authenticated profile to the workspace. By default, configured for all workspace events (`ALL` type). Prerequisites: workspace must exist.

Query parameters:

| Parameter | Required | Format | Default | Description |
|---|---|---|---|---|
| `allMembers` | No | Boolean | `false` | Whether to subscribe the workspace to workspace events, enabling workspace-wide notifications for all members by default (workspace owner only) |

Response: `200 OK`, Subscription with HAL links.

**POST** `/api/channels/{channel-id}/subscriptions` — Subscribe to a channel.
Subscribes the authenticated profile to the channel. By default, configured for all channel events. Prerequisites: channel must exist.

Query parameters: `allMembers` (No, Boolean, default `false`) — whether to subscribe the workspace to channel events, enabling notifications for all members by default (workspace owner only).

Response: `200 OK`, Subscription with HAL links.

**POST** `/api/datasets/{dataset-id}/subscriptions` — Subscribe to a dataset.
Subscribes the authenticated profile to the dataset. By default, configured for all dataset events. Prerequisites: dataset must exist.

Query parameters: `allMembers` (No, Boolean, default `false`) — whether to subscribe the workspace to dataset events, enabling notifications for all members by default (workspace owner only).

Response: `200 OK`, Subscription with HAL links.

**POST** `/api/pipelines/{pipeline-id}/subscriptions` — Subscribe to a pipeline.
Subscribes the authenticated profile to the pipeline. By default, configured for all pipeline events. Prerequisites: pipeline must exist.

Query parameters: `allMembers` (No, Boolean, default `false`) — whether to subscribe the workspace to pipeline events, enabling notifications for all members by default (workspace owner only).

Response: `200 OK`, Subscription with HAL links.

**PUT** `/api/subscriptions/{subscription-id}` — Update a subscription.
Prerequisites: subscription must exist. Body: `{ "type": "<Subscription Type>" }`. Response: `200 OK`, Subscription with HAL links.

**DELETE** `/api/subscriptions/{subscription-id}` — Remove a subscription.
Prerequisites: subscription must exist. Response: `204 No Content`.

---

## Tags

Tags are hash-prefixed keywords or phrases that appear in the title, description, or comments of a dataset. Tags can be used to index datasets by their contained tags with a search, allowing topical dataset categorisation.

### Object: Tag

| Path | JSON Type | Format | Description |
|---|---|---|---|
| `id` | `string` | Version 4 UUID | The tag ID |
| `name` | `string` | | The tag name |
| `usage` | `number` | Unsigned integer | Number of times the tag is used within the workspace |

### Endpoints

**GET** `/api/workspaces/{workspace-id}/tags` — View all tags in a workspace.
Prerequisites: workspace must exist. Response: `200 OK`, Tag collection with HAL links.

**GET** `/api/workspaces/{workspace-id}/news/tags` — View all tags in the news for a workspace.
Prerequisites: workspace must exist. Response: `200 OK`, Tag collection with HAL links.

**GET** `/api/workspaces/{workspace-id}/tags/{tag-id}` — View a tag in a workspace.
Prerequisites: workspace must exist; tag must exist. Response: `200 OK`, Tag with HAL links.

**See also:** [Search for datasets in a workspace by tag name](#search).

---

## Workspaces

Workspaces allow users to operate within isolated instances of the Meltano Cloud service. This is useful for separating profiles based on the data they require access to.

### Object: Workspace

| Path | JSON Type | Format | Description |
|---|---|---|---|
| `id` | `string` | Version 4 UUID | The workspace ID |
| `created` | `string` | ISO 8601 timestamp | The instant the workspace was created |
| `lastModified` | `string` | ISO 8601 timestamp | The instant the workspace was last modified |
| `alias` | `string` | | The workspace alias and database schema name |
| `name` | `string` | | The workspace name |
| `domains` | `string[]` | Array of domain hosts | The workspace allowed domains |
| `repositoryUrl` | `string` | URL | The workspace repository URL |
| `pipelinesImage` | `string` | Container image name path | The path name of an image to run pipelines from |
| `imageUrl` | `string` | Image [data URL](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URIs) | The workspace image data URL |
| `status` | `string` | [Workspace Status](#workspace-status) | The workspace status |
| `defaultWorkspace` | `bool` | | Whether or not the workspace is set as the default for the authenticated user |

#### Format: Workspace Status {#workspace-status}

`string` — one of:

| Value | Description |
|---|---|
| `READY` | The workspace completed processing resource changes |
| `PROVISIONING` | The workspace is processing resource changes |
| `FAILED` | The workspace failed to process resource changes |

### Endpoints

**GET** `/api/workspaces` — View all workspaces.
Returns all workspaces the authenticated profile is an owner or member of. Response: `200 OK`, Workspace collection with HAL links.

**GET** `/api/workspaces/{workspace-id}` — View a workspace.
Prerequisites: user must be a member of the workspace. Response: `200 OK`, Workspace with HAL links.

**POST** `/api/workspaces` — Initialise a workspace.
Response: `200 OK`, Workspace with HAL links.

**PUT** `/api/workspaces/{workspace-id}` — Create a workspace.
Prerequisites: user must be the owner of the workspace; the workspace must have been initialised in order to create it. Body: Workspace resource. Response: `201 Created`, Workspace with HAL links.

**PUT** `/api/workspaces/{workspace-id}` — Update a workspace.
Prerequisites: user must be the owner of the workspace; the workspace must have been created in order to update it. Body: Workspace resource. Response: `200 OK`, Workspace with HAL links.

**DELETE** `/api/workspaces/{workspace-id}` — Delete a workspace.
Prerequisites: user must be the owner of the workspace. Response: `204 No Content`.

**See also:** [Transfer a workspace](#accounts), [Set a workspace as default](#profiles), [View/create/cancel invitations to a workspace](#invitations), [View members of a workspace](#members), [View all channels in a workspace](#channels), [View all liked datasets in a workspace](#datasets), [View the feed of a workspace](#feed), [Pipelines in a workspace](#pipelines), [View all jobs for a workspace](#jobs), [WorkspaceML](/reference/cloud/dataml/workspaceml/).
