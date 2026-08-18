# Workspaces

How to create, configure, and manage a Meltano Cloud workspace, including environments, DataOps promotion, custom pipeline images, and inviting members.

## What is a workspace

A **workspace** is your isolated data environment in Meltano — think of it as a dedicated project folder for a team, client, or use case. Each workspace has its own pipelines, data sources, data store connections, and configuration, all backed by a Git repository.

You can be a member of multiple workspaces and each one operates independently.

### Before you begin

You need a Meltano account to create a workspace. If you don't have one yet, book a call with Meltano at [meltano.com](https://meltano.com).

## Creating a workspace

### Option 1 — Empty workspace (recommended for new projects)

When you sign in to Meltano for the first time, you'll be prompted to create your first workspace automatically.

To create additional workspaces:

1. Make sure you're logged in to Meltano and then open the workspace selector from the top navigation bar.
2. Click **New Workspace**.
3. Fill in the **Name** field — this is how you'll identify the workspace across the platform.
4. *(Optional)* Add **Approved Domains** to restrict membership to users with a specific email domain (e.g. `yourcompany.com`).
5. Click **Continue**.

Your workspace is ready. You can now create a data import pipeline or manage your workspace via the Lab or API.

### Option 2 — From an existing GitHub repository

If you already have a Meltano project in a GitHub repository — or a project previously created in Matatika — you can import it directly.

1. On the new workspace screen, expand the **Advanced** section.
2. Paste your GitHub repository **URL** into the field provided.
3. *(Optional)* Specify a **branch** if you want to use something other than the default branch.
4. Click **Continue**.

Meltano will scaffold your workspace using the configuration from that repository. Once created, the workspace Lab manages your configuration independently of the source repo — changes you make in the UI won't automatically push back to the original repository.

This works with any repository created by Matatika or any existing Meltano project.

## Managing your workspace

Once a workspace exists, you can manage it through three surfaces:

| Surface | Best for |
|---|---|
| **Meltano Lab** (UI) | Day-to-day pipeline management, exploring data, adding connectors |
| **Meltano API** | Programmatic access, automation, CI/CD integrations |
| **VS Code (local)** | Running pipelines locally, editing config files directly |

### Workspace settings (quick access)

Access workspace settings by clicking your **profile image** (top-right) and selecting **Settings**. From here you can:

- Rename your workspace
- Copy the backing GitHub repository URL (useful for local development)
- Manage approved domains and member access

### Running pipelines locally

Every Meltano workspace is backed by a GitHub repository. To run pipelines on your own machine:

1. In the Meltano app, go to **Settings** and copy the repository URL.
2. Clone it locally:
   ```bash
   git clone https://github.com/your-org/your-workspace
   ```
3. Change into the cloned directory and create a `.env` file with your credentials.
4. Navigate to **Lab → Pipelines**, expand the pipeline you want to run, and follow the local run instructions shown there.

Prerequisites for local runs: **Git**, **Python ≥ 3.8**, and **Meltano** installed. A virtual environment is strongly recommended.

### Workspace concepts

| Concept | What it means |
|---|---|
| **Git-backed config** | Every change made in the UI is committed to a single Git repository. The UI is a reflection of what's in Git — not the other way around. |
| **Isolated data store** | Each workspace connects to its own data warehouse (Snowflake, Redshift, Azure Synapse, etc.) and cannot access another workspace's data. |
| **Role-based access** | Members can be assigned as **Owner**, **Administrator**, or **Member**. |
| **Approved Domains** | Optionally restrict who can join the workspace by email domain. |

---

## Managing config from GitHub

**Time required: 5 minutes**

### Prerequisites

You must have:

- Admin or owner access to the workspace you want to configure
- Admin rights to the workspace GitHub repository (available on Meltano premium plans)

### Overview

Meltano supports a full DataOps lifecycle where all of your workspace configuration is version-controlled in a GitHub repository. When you push a change to that repository, a **deployment** can be triggered automatically to sync those changes into your live workspace.

Think of it like a direct line from your code editor to your running workspace. You make a change, push it to GitHub, and Meltano picks it up without any manual steps in between.

There are two ways to trigger a deployment:

- **GitHub Webhook** (covered below): every push to the repository automatically deploys your workspace
- **Manual deployment**: use the Meltano API or Postman collection to trigger a deployment on demand

### Setting up a GitHub Webhook

A webhook is a notification that GitHub sends to Meltano the moment you push new code. Meltano receives that notification and immediately redeploys your workspace using the latest configuration.

#### Step 1 — Find your workspace ID

1. Open your workspace in Meltano.
2. Look at the URL in your browser. It will contain a UUID that looks like this: `https://app.meltano.com/workspaces/e8e23b01-1eca-4021-a054-dc653756b4cd`
3. Copy that UUID. This is your `workspace_id`.

#### Step 2 — Find your deployment secret

1. In your workspace, open **Settings** from the left navigation bar.
2. Locate the **Deployment Secret** field and copy its value.

#### Step 3 — Add the webhook in GitHub

1. Navigate to your workspace repository on GitHub.
2. Go to **Settings** from the left navigation bar > **Webhooks** > **Add webhook**.
3. Fill in the fields as follows:

| Field | Value |
|---|---|
| Payload URL | `https://app.meltano.com/api/workspaces/<workspace_id>/deployments/github-webhook` |
| Content type | `application/json` |
| Secret | Your Deployment Secret from Step 2 |

4. Click **Add webhook**.

From this point on, every push to your workspace repository will automatically trigger a deployment and update your live workspace.

### Triggering a manual deployment

If you prefer to deploy on demand rather than on every push, you can use the Meltano API. The Deployments API reference and the Postman collection both support this.

This setup is most useful when your workspace configuration is managed by a team and you want every approved merge to automatically roll out to your workspace, reducing the chance of config drift between what is in GitHub and what is actually running.

---

## Managing config with environments

**Time required: 5 minutes**

### Overview

Every Meltano workspace is backed by [Meltano environments](https://docs.meltano.com/concepts/environments), a way to keep separate configuration for different stages of your data work, such as development, staging, and production. Each environment can have its own connector settings, credentials, and plugin config, all stored in your `meltano.yml` file.

When a workspace loads, it reads from whichever environment is currently set as the default. Changing the default environment swaps out the configuration that all pipelines in that workspace will use.

Three environments are created automatically when a workspace is set up:

- `dev` (default)
- `staging`
- `prod`

### How configuration works in `meltano.yml`

Configuration is layered. Each environment block can override specific settings from the base plugin definition. If a setting is not specified in the active environment, the base value is used as a fallback.

Here is an example using `tap-auth0` across three environments:

```yaml
version: 1
default_environment: dev
project_id: 8c07f654-6908-4b51-acef-8de3d37aecac
environments:
  - name: dev
    config:
      plugins:
        extractors:
          - name: tap-auth0
            config:
              client_id: 39Pu9tTomnTv594VAFYnmRvkEpSlI7a6
  - name: staging
    config:
      plugins:
        extractors:
          - name: tap-auth0
            config:
              client_id: 4Zd5QXqHKNoKq4ySx8CP1UBm5eIUgh7t
  - name: prod
    config:
      plugins:
        extractors:
          - name: tap-auth0
            config:
              client_id: u4kcVHKUD9lkbUbXA3eXCt88scStaqHM
              domain: matatika.eu.auth0.com
plugins:
  extractors:
    - name: tap-auth0
      config:
        domain: matatika-staging.eu.auth0.com
```

Here is what gets loaded depending on which environment is active:

| Active environment | `client_id` | `domain` |
|---|---|---|
| `dev` | `39Pu9tTomnTv594VAFYnmRvkEpSlI7a6` | `matatika-staging.eu.auth0.com` (from base) |
| `staging` | `4Zd5QXqHKNoKq4ySx8CP1UBm5eIUgh7t` | `matatika-staging.eu.auth0.com` (from base) |
| `prod` | `u4kcVHKUD9lkbUbXA3eXCt88scStaqHM` | `matatika.eu.auth0.com` (from `prod` override) |

Notice that `prod` is the only environment with its own `domain` value. For `dev` and `staging`, the domain falls back to what is defined in the base `tap-auth0` block.

### Switching the active environment

The active environment is initially set by the `default_environment` property in your `meltano.yml`. You can change it at any time from the workspace UI:

1. Open the workspace drop-down menu.
2. Select **Settings**.
3. Update the **Active environment** field to the environment you want.
4. Click **Save**.

Once saved, all pipelines in the workspace will load configuration from the newly selected environment. To verify what values a pipeline will use at runtime, open the pipeline and check the **Environment** tab.

Note: Switching environments changes the configuration loaded for every pipeline in the workspace. If you are running a shared workspace, make sure your team is aware before making this change.

---

## Promoting changes with DataOps

**Time required: 10 minutes**

### Overview

DataOps is an agile approach to managing data pipelines with the same discipline applied to software development: test changes before they reach production, promote them through defined stages, and keep a full history of what changed and when.

In Meltano, you implement this by creating separate workspaces for each stage of your pipeline lifecycle — one for development, one for staging, and one for production. Each workspace points at the same underlying GitHub repository but operates on a different branch or merge state, and runs with its own active environment configuration.

### Setting up a three-workspace DataOps workflow

#### Step 1 — Create your workspaces

Create three separate workspaces to represent each stage:

**Development workspace** (e.g. `My Workspace (dev)`):
1. Open the workspace drop-down menu.
2. Select **New workspace**.
3. Enter a name in the **Name** field.
4. Click **Save**.

**Staging workspace** (e.g. `My Workspace (staging)`):

Repeat the steps above with a staging-appropriate name.

Then set the active environment to `staging`:
1. Open the drop-down menu and select **Settings**.
2. Set **Active environment** to `staging`.
3. Click **Save**.

**Production workspace** (e.g. `My Workspace`):

Repeat the workspace creation steps, then set the active environment to `prod` following the same process.

#### Step 2 — Develop and test in dev

Make all changes and run your pipelines in the development workspace. The repository URL for each workspace can be found in its **Settings** page.

#### Step 3 — Promote dev changes to staging

Once your changes are tested in dev, merge them into the staging workspace repository:

```bash
git clone git@github.com:YourOrg/My-Workspace-staging-kklcdol
cd My-Workspace-staging-kklcdol

git remote add dev git@github.com:YourOrg/My-Workspace-dev-zgtzhjd
git pull -X theirs --allow-unrelated-histories dev main

# review the changes before pushing
git push
```

Caution: the `-X theirs` flag tells Git to prefer the incoming changes from the dev branch when there are conflicts. Review the result carefully before pushing to make sure nothing unexpected was overwritten.

#### Step 4 — Promote staging changes to production

Once staging has been validated, merge into the production workspace repository:

```bash
git clone git@github.com:YourOrg/My-Workspace-setarqi
cd My-Workspace-setarqi

git remote add staging git@github.com:YourOrg/My-Workspace-staging-kklcdol
git pull -X theirs --allow-unrelated-histories staging main

# review the changes before pushing
git push
```

If you have a GitHub Webhook configured on any of these workspaces, pushing will automatically trigger a deployment. See the "Managing config from GitHub" section above for setup instructions.

Why this pattern works: each workspace is isolated. Development activity cannot affect production data. Promotions happen through Git, so every change is auditable and reversible. Combining this with environment-specific configuration means credentials and connection details are always appropriate for the stage being run.

---

## Running pipelines with a custom image

**Time required: 10 minutes**

### Prerequisites

You must have:

- A Meltano account
- Meltano deployed in your own cloud environment

### Overview

By default, when a pipeline runs in Meltano, the platform spins up a container that clones your workspace repository, installs all the required plugins, and then executes your pipeline. This works well for most cases, but it adds startup time every single run.

A **custom pipelines image** lets you pre-bake that setup work into a Docker image at build time. When the pipeline runs, the container starts from your pre-built image and skips the install step entirely. The result is noticeably faster pipeline execution, especially for workspaces with many plugins or large dependencies.

You can also use a custom image to bring in packages, system dependencies, or custom scripts that the default base image does not include.

#### Step 1 — Point Meltano at your container registry

In your catalog deployment environment, set the `MELTANO_DATAFLOW_DOCKERREGISTRY` variable to the registry where your custom image will be stored:

```bash
# Private Azure Container Registry
MELTANO_DATAFLOW_DOCKERREGISTRY=meltano.azurecr.io

# Docker Hub
MELTANO_DATAFLOW_DOCKERREGISTRY=docker.io
```

#### Step 2 — Write a Dockerfile for your workspace

The only hard requirement is that your workspace directory must be set as the working directory inside the image. Everything else can be customised to your needs.

**Minimal example:**

```dockerfile
RUN mkdir workspace
WORKDIR /workspace

COPY . .
```

**Example with pre-installed plugins:**

This is the most common pattern. Pre-running `meltano install` at build time means your plugins are already installed when the container starts, removing that step from each pipeline run.

```dockerfile
FROM meltano.azurecr.io/meltano/meltano-catalog-shelltask:latest-dev

RUN mkdir workspace
WORKDIR /workspace

COPY . .

RUN meltano install

# Remove pip temporary files to keep the image size smaller
RUN rm -rf ~/.cache
```

A working reference example is available in the [`example-github-analytics`](https://github.com/Matatika/example-github-analytics/blob/2b0966d9f2fd5b6563d013edde65b8b5a98fe7bc/Dockerfile) repository.

#### Step 3 — Build and push the image

Build your image locally and push it to the registry you configured in Step 1:

```bash
docker build -t <registry host>/<image name> .
docker push <registry host>/<image name>
```

The `<image name>` here must match the value you set for `pipelines_image` in your `workspace.yml`:

```yaml
pipelines_image: <image name>
```

You can see how this is wired together in the `example-github-analytics` reference files:
- [`workspace.yml`](https://github.com/Matatika/example-github-analytics/blob/2b0966d9f2fd5b6563d013edde65b8b5a98fe7bc/workspace.yml#L3)
- [`azure-pipelines.yml`](https://github.com/Matatika/example-github-analytics/blob/2b0966d9f2fd5b6563d013edde65b8b5a98fe7bc/azure-pipelines.yml#L11-L15)

For teams running frequent deployments, consider adding a CI step (such as an Azure Pipelines or GitHub Actions workflow) that automatically builds and pushes a new image whenever the workspace repository changes. This keeps your custom image in sync with your configuration without manual intervention.

---

## Controlling the Lab landing page

**Time required: 2 minutes**

### Overview

`HOME_PAGE` is an `app_properties` key in `workspace.yml` that forces every member landing in the Lab to a specific app (e.g. `dashboard`) instead of the first item in the app's menu.

```yaml
app_properties:
  HOME_PAGE: dashboard
```

### When to remove it

By default, Switch to App already lands members on the first menu item defined in `APP_MENU_ITEMS`, so `HOME_PAGE` is only needed when you want to override that default. If members are getting stuck on a single app (e.g. the Elementary dashboard) and can't navigate to the rest of the Lab, removing `HOME_PAGE` restores normal navigation.

### How to remove it

1. Open `workspace.yml`.
2. Delete the `HOME_PAGE` line from `app_properties`.
3. Deploy the workspace.

```yaml
app_properties:
  # HOME_PAGE removed, members now land on the first menu item
```

---

## Workspace settings reference

Navigate to **Workspace → Settings** from the left navigation bar to manage your workspace configuration — from basic identity settings to repository connections, security credentials, and external log streaming.

### General

**Name**
- Give your workspace a name that your users will instantly recognise.
- Note: Renaming the workspace also renames the associated repository. This may break any automation you have already configured that references the old name.

**Approved Domains**
- Control who can be invited to your workspace by specifying a list of approved email domains.
- Users can only send invitations to people whose email addresses belong to the listed domains.
- Leave this field empty to allow invitations to any domain.

**Image**
- Upload a workspace image to help members quickly confirm they are in the right workspace.
- A recognisable logo or avatar is especially useful in workspaces shared across multiple teams.

**Active Environment**
- Set the name of the environment whose configuration your workspace should use.
- The environment must already exist in your `meltano.yml` file under the `environments` section.
- See the [Environments documentation](https://docs.meltano.com/concepts/environments) for more information.

### Repository & Credentials

These fields connect your workspace to its underlying Git repository and control secure access.

- **Repo URL**: The URL of the repository linked to this workspace.
- **Repository Branch**: The branch your workspace is currently tracking. Click the copy icon to copy the branch name.
- **Repository Directory**: The root directory within the repository used by this workspace. Click the copy icon to copy the path.
- **SSH Private Key**: The private key used for repository authentication. Click the copy icon to copy the key value.
- **GitHub Installation ID**: The ID associated with your GitHub App installation for this workspace.
- **Deployment Secret**: A secret token used to authenticate deployments.
  - Click the copy icon to copy the current secret.
  - Click **Regenerate** to generate a new secret. Use this when rotating credentials or if a secret is compromised.

### Delete Workspace

- Click the **Delete** button to permanently remove this workspace.
- A confirmation modal will appear with the message "This action cannot be undone."
- Click **Delete** in the modal to confirm, or **Close** to cancel and return to settings.

Deletion is irreversible. Ensure you have backed up any important data or configuration before proceeding.

---

## Invite & manage members

Navigate to your workspace and click **Invite others** from the sidebar to open the Invitations page.

Use this section to bring teammates into your workspace — whether you're onboarding a new data engineer, giving a stakeholder read access, or rotating collaborators on a project.

### Send an invitation

1. Click **Add Invitation**.
2. Enter one or more email addresses in the email field — separate multiple emails with a comma.
3. Select their role.
4. Click **Send**.

They'll each receive an email with a link to join your workspace.

Inviting a whole team at once? Enter all their emails in one go — e.g. `alice@company.com, bob@company.com, carol@company.com` — and send a single batch invite.

Invited members must accept the invitation before they can access the workspace. Until then, their status will show as **Pending**.

### Manage pending invitations

Once an invite is sent, it appears in the **Pending** list. From the three-dot menu next to any invite, you can:

| Action | When to use it |
|---|---|
| **Resend** | The teammate didn't receive the email or the link expired |
| **Revoke** | You want to cancel the invite before they accept |
| **Delete** | You want to remove the invite record from the list entirely |

Revoking an invite invalidates the link immediately. The teammate will not be able to join using the original email — you'll need to send a new invite if needed.

### Invitation status

| Status | What it means |
|---|---|
| **Pending** | Invite sent, waiting for the teammate to accept |
| **Accepted** | Teammate has joined the workspace |

Once a teammate accepts the invite, their status updates automatically and they appear under **Members**.

If you're setting up a new workspace, invite your team early so they can configure their own credentials and access pipelines as soon as they're ready.
