# WorkspaceML

Reference for the workspace configuration file (`workspace.yml`) that defines a Meltano Cloud workspace as code, including dashboard and invitation customisation.

## Overview

The workspace file is stored in YAML format. Use it to configure your workspace as code.

### Example: `workspace.yml`

```yaml
version: workspaces/v0.2
name: My workspace
domains:
  - meltano.com
  - example.co.uk
default_data_store: Warehouse
state_data_store: Warehouse
dataset_paths:
  - analyze/datasets
  - .meltano/analyze/datasets
channel_paths:
  - analyze/channels
pipeline_paths:
  - pipelines
plugin_paths:
  - plugins
data_store_paths:
  - datastores
app_properties:
  WELCOME_DATASET_ALIAS: analyze/datasets/welcome
  WELCOME_MESSAGE: Welcome to the workspace
  FEED_VIEW_DEFAULT: listView
  DATASET_WATCH_ALERTS_ALT_TEXT: Select to receive summary of dataset updates
  DATASET_WATCH_ALL_ACTIVITY_ALT_TEXT: Select to receive updates and discussion from this dataset
  DATASET_ASSISTANT_TAB_ALERTS_ALT_TEXT: Updates
  DATASET_ASSISTANT_NO_ALERTS_ALT_TEXT: No updates
  NEWS_DATASET_ALERT_ALT_TEXT: Update
  HELP_DATASET_ALIAS: analyze/datasets/more_information
  TOOLBAR_SEARCH_ALT_TEXT: Search all datasets...
  HOME_PAGE: news
  MENU_ITEM_HOME_ALT_TEXT: My Updates
  MENU_ITEM_CHANNELS_ALT_TEXT: Lists
  MENU_ITEM_HELP_ALT_TEXT: More Information
  HELP_CUSTOM_FA_MENU_ICON: acorn
  ALERTS_HELP_TEXT: Watch for alerts or all activity.
  DISCUSSION_HELP_TEXT: Talk about this dataset!
  RELATED_HELP_TEXT: Datasets related to this one.
  DATASET_VIEW_TABS: alerts,discussion,related
  APP_MENU_ITEMS: '[{"name": "explore", "faIcon": "users", "label": "Profiles"}, {"name": "library", "faIcon": "list"}, {"name": "starred", "faIcon": "star"}]'
  LIBRARY_LIST_INFO_ITEM_TEXT: Profile(s)
  DATASET_ACTIONS: star,share,table,save
  MEMBER_COMMENTS_READ_ONLY: true
  MEMBER_COMMENTS_READ_ONLY_MESSAGE: Comments are set to read-only
  INVITATION_EMAIL_RESULT_URL: https://meltano.com/slack
  INVITATION_EMAIL_SUBJECT: You have been invited to a workspace
  INVITATION_EMAIL_TEMPLATE: |-
    <!DOCTYPE html>
    <html xmlns:th="http://www.thymeleaf.org">
    <head>
    </head>
    <body>
      <h2 th:inline="text">[[${invitationCreatorName}]] ([[${invitationCreatorEmail}]]) has
        invited you to the '[[${workspaceName}]]' Workspace.</h2>

      <p>
        <a th:href="${passwordResetTicketUrl}">Accept invitation</a>
      </p>

      <br />
      <hr style="border: 2px solid #EAEEF3; border-bottom: 0;" />
    </body>
    </html>
  DASHBOARD_PAGE_TITLE: Data Observability Dashboard
  DASHBOARD_CONTENT: |-
    <div style={{'display':'flex', 'justify-content': 'center'}}>
        <div style={{'border-right': '2px solid #D3D3D3'}}>
            <h2>Test results breakdown</h2>
            <DatasetChart alias="data-observability/test-results-breakdown"/>
        </div>
        <div>
            <h2>Tables health</h2>
            <DatasetLink alias="data-observability/table-health-breakdown">
                <DatasetChart alias="data-observability/tables-health" />
            </DatasetLink>
        </div>
    </div>
```

### Top-Level Fields

| Path | JSON Type | Description |
|---|---|---|
| `version` | `string` | The version identifies this artifact type. |
| `name` | `string` | Name of your workspace. |
| `default_data_store` | `string` | Name of your workspace's default data store (see DatastoreML). This controls the default for loading, query, transformation, and state (unless overridden with `state_data_store`). |
| `state_data_store` | `string` | Name of your workspace's state data store (see DatastoreML). This controls where pipeline state is stored and **must** reference a Postgres, BigQuery or Snowflake database (defaults to the managed warehouse data store, same as `default_data_store`). |
| `pipelines_image` | `string` | The path name of an image to run pipelines from. |
| `image_url` | `string` | The Meltano tasks that will be run. |
| `dataset_paths` | `string[]` | Paths for your workspace to deploy datasets from. |
| `channel_paths` | `string[]` | Paths for your workspace to deploy channels from. |
| `pipeline_paths` | `string[]` | Paths for your workspace to deploy pipelines from. |
| `plugin_paths` | `string[]` | Paths for your workspace to deploy plugins from. |
| `app_properties` | `object` | A map of optional properties to customize your workspace (see the example above and the Dashboards / Invitations sections below). |

### Environment-Specific Workspace Configuration

Workspace configuration files with a `-*` suffix (e.g. `workspace-dev.yml`) define environment-specific workspace configuration. During deployment of a workspace, the base `workspace.yml` configuration is loaded, followed by a `workspace-*.yml` matching the active environment (if present).

Environment-specific workspace configuration files only need to contain the properties a user wants to override from `workspace.yml` (`version` is required regardless).

`workspace.yml`:

```yaml
version: workspaces/v0.2
name: My workspace
domains:
  - meltano.com
  - example.co.uk
default_data_store: Warehouse
state_data_store: Warehouse
dataset_paths:
  - analyze/datasets
  - .meltano/analyze/datasets
channel_paths:
  - analyze/channels
pipeline_paths:
  - pipelines
plugin_paths:
  - plugins
data_store_paths:
  - datastores
```

`workspace-dev.yml`:

```yaml
version: workspaces/v0.2
name: My workspace (dev)
pipelines_image: my-workspace-image:latest-dev
```

Further reading: Workspaces API resource (`/reference/cloud/api/resources/workspaces`).

---

## Dashboards

Dashboards allow you to design a layout for data and datasets in your workspace. These are fully customizable and render custom HTML and CSS, letting you format them as required.

You create dashboards of your datasets in the Matatika app by defining a few settings and then providing your dashboard content in your workspace's `workspace.yml` file.

### Example `workspace.yml` (dashboard configuration)

```yaml
version: workspaces/v0.2
name: My workspace
domains:
  - meltano.com
  - example.co.uk
default_data_store: Warehouse
state_data_store: Warehouse
dataset_paths:
  - analyze/datasets
  - .meltano/analyze/datasets
channel_paths:
  - analyze/channels
pipeline_paths:
  - pipelines
plugin_paths:
  - plugins
data_store_paths:
  - datastores
app_properties:
  WELCOME_DATASET_ALIAS: welcome
  DASHBOARD_PAGE_TITLE: Data Observability Dashboard
  DASHBOARD_CONTENT: |-
    <div style={{'display':'flex', 'padding-bottom': '30px', 'justify-content': 'center'}}>
        <div style={{'border-right': '2px solid #D3D3D3'}}>
            <h2>Test results breakdown</h2>
            <DatasetChart alias="data-observability/test-results-breakdown"/>
        </div>
        <div>
            <h2>Tables health</h2>
            <DatasetLink alias="data-observability/table-health-breakdown">
                <DatasetChart alias="data-observability/tables-health" />
            </DatasetLink>
        </div>
    </div>
  APP_MENU_ITEMS: |-
    [
      {"name": "dashboard", "faIcon": "chart-bar", "label": "Dashboard"},
      {"name": "explore", "faIcon": "hashtag", "label": "Explore"},
      {"name": "channels", "faIcon": "database", "label": "Channels"},
      {"name": "library", "faIcon": "list", "label": "Library"},
      {"name": "starred", "faIcon": "star", "label": "Starred"},
      {"name": "help", "faIcon": "question-circle", "label": "Help"}
    ]
default_data_store: Warehouse
dataset_paths:
  - analyze/datasets
  - .meltano/analyze/datasets
channel_paths:
  - analyze/channels
pipeline_paths:
  - pipelines
plugin_paths:
  - plugins
data_store_paths:
  - datastores
```

### Dashboard Settings

These settings are nested under `app_properties`.

| Setting | Description |
|---|---|
| `DASHBOARD_PAGE_TITLE` | Dashboard page title. |
| `DASHBOARD_CONTENT` | Your dashboard content as HTML. |
| `APP_MENU_ITEMS` | Currently you have to provide an override for all pages showing in the app, including your new dashboard page. |

A list of `faIcons` for your dashboard can be found at FontAwesome Icons v5 (https://fontawesome.com/v5/search). You can use any free icons as your dashboard icon, or to change the icon of an existing page.

### Dashboard Components

#### `DatasetChart`

Allows you to choose any dataset in your workspace by its alias, and render it on your dashboard.

| Prop | Type | Description | Required | Default |
|---|---|---|---|---|
| `alias` | String | The dataset alias to fetch for render | If `dataset` not specified | |
| `dataset` | Object | The dataset to render | If `alias` not specified | |
| `showTable` | Boolean | Show the dataset data as a table | No | `false` |

#### `DatasetData`

Allows you to render custom JSX in the context of a dataset and its data.

| Prop | Type | Description | Required | Default |
|---|---|---|---|---|
| `alias` | String | The dataset alias to fetch for render | If `dataset` not specified | |
| `dataset` | Object | The dataset to render | If `alias` not specified | |
| `render` | Function | The JSX content to render (args: `dataset`, `data`) | Yes | |

#### `DatasetLink`

Wraps elements or text and creates an internal link to a dataset in your workspace (no page reload).

| Prop | Type | Description | Required | Default |
|---|---|---|---|---|
| `alias` | String | The dataset alias | Yes | |

#### `Back`

Renders a back button.

#### `DownloadDataset`

Download a dataset from the workspace.

| Prop | Type | Description | Required | Default |
|---|---|---|---|---|
| `alias` | String | The dataset alias to fetch for render | If `dataset` not specified | |
| `dataset` | Object | The dataset to render | If `alias` not specified | |
| `tooltip` | String | The text displayed on hover | No | `Download {dataset title OR dataset alias}` |

#### `DownloadResource`

Download a resource from the workspace.

| Prop | Type | Description | Required | Default |
|---|---|---|---|---|
| `path` | String | The resource path | Yes | |
| `tooltip` | String | The text displayed on hover | No | `Download {path}` |

---

## Invitations

Invitations allow you to customise the onboarding experience for new members of your workspace. All settings below are nested under `app_properties`.

### Result URL — `INVITATION_EMAIL_RESULT_URL`

The URL a user will be redirected to after accepting the workspace invitation.

```yaml
app_properties:
  INVITATION_EMAIL_RESULT_URL: https://meltano.com/slack
```

### Subject — `INVITATION_EMAIL_SUBJECT`

The subject of the invitation email. Templating is not yet supported (as defined below).

```yaml
app_properties:
  INVITATION_EMAIL_SUBJECT: You have been invited to a workspace
```

### Template — `INVITATION_EMAIL_TEMPLATE`

The invitation email template HTML, processed by Thymeleaf (https://www.thymeleaf.org/doc/tutorials/3.0/usingthymeleaf.html).

```yaml
app_properties:
  INVITATION_EMAIL_TEMPLATE: |-
    <!DOCTYPE html>
    <html xmlns:th="http://www.thymeleaf.org">
    <head>
    </head>
    <body>
      <h2 th:inline="text">[[${invitationCreatorName}]] ([[${invitationCreatorEmail}]]) has
        invited you to the '[[${workspaceName}]]' Workspace.</h2>

      <p>
        <a th:href="${passwordResetTicketUrl}">Accept invitation</a>
      </p>

      <br />
      <hr style="border: 2px solid #EAEEF3; border-bottom: 0;" />
    </body>
    </html>
```

#### Template Variables

| Name | Description |
|---|---|
| `invitationCreatorName` | The name of the invitation creator profile. |
| `invitationCreatorEmail` | The email of the invitation creator profile. |
| `workspaceName` | The name of the workspace invited to. |
| `passwordResetTicketUrl` | The link to accept the invitation (this should be accessible for a user to be able to accept). |

Inlining (https://www.thymeleaf.org/doc/tutorials/3.0/usingthymeleaf.html#inlining) is recommended when using variables, where possible (see the example above).

---

## Further Reading

- Workspaces API resource: `/reference/cloud/api/resources/workspaces`
