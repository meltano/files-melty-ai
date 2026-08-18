# Operations

Diagnosing failing pipelines, routing logs to external monitoring, managing account/profile security, and setting up a local development environment for a Meltano Cloud workspace.

## Setup your development environment

**Time required: 10 minutes**

### Prerequisites

You must have [`git`](https://github.com/git-guides/install-git) installed, or [GitHub Desktop](https://desktop.github.com/) if you prefer a visual interface.

### Overview

Within an organisation, importing and transforming data into analytics-ready models requires careful collaboration across code artifacts such as sources, pipelines, models, and datasets. To manage these changes safely, teams need to develop and test in an isolated environment before promoting anything to production.

A Meltano workspace manages the configuration of your project for a specific environment, and all project code is committed to a Git repository with full version control. Keeping environments separate means you can have dedicated spaces for development, testing, and stable production workloads. This model is portable by design: you can clone a workspace repository locally, make changes using standard `meltano` commands, and push those changes back to have them automatically deployed.

### Working with Meltano locally

A Meltano workspace project is a standard Meltano project and can be treated as one. Once the workspace repository has been cloned to your local machine, you can run any `meltano` command against it as normal. Common use cases include:

- Adding or updating plugin configuration in `meltano.yml`
- Running a pipeline manually with `meltano run` to test it before it goes on a schedule
- Debugging extraction or loading issues without affecting the live workspace

Any changes you make locally can be committed and pushed back to the remote repository. If you have a GitHub Webhook configured, those changes will be picked up and deployed to your workspace automatically. See the "Managing Config from GitHub" section of the Workspaces guide for setup instructions.

### Using VS Code

VS Code can be used as a full development environment for your workspace. Meltano workspaces support a dev container configuration, which means VS Code can spin up a properly configured container environment with a single click.

#### Setup steps

1. Clone your workspace repository and open the folder in VS Code:

```bash
git clone https://github.com/YourOrg/your-workspace
code your-workspace
```

2. VS Code will detect the dev container configuration and display a pop-up: "Folder contains a Dev Container configuration file. Reopen folder to develop in a container." Click **Reopen in Container**.

Alternative way to open: if the pop-up does not appear, click the **Open a Remote Window** button in the bottom-left corner of VS Code, then select **Reopen in Container** from the command palette.

3. Once the container environment has finished initialising, VS Code will be mounted at the `workspaces` directory. From here you can clone additional workspaces, make changes, and commit and push directly within VS Code.

About DataML artifacts: Meltano workspace repositories contain deployable entities defined as Data Management Language (DataML) artifacts, alongside standard Meltano plugin `.lock` files, `meltano.yml` schedules, jobs, plugins, and configuration. All of these are interpreted as Meltano entities when the workspace is deployed.

---

## Pipeline diagnosis

When something goes wrong with a pipeline, you have two ways to figure out why: dig into the job run logs directly, or let Melty AI read the failure and explain it in plain language.

### Diagnosing pipeline runs and logs

Every pipeline in your workspace can be inspected directly from the **Pipelines** view, without needing Melty AI. Each pipeline card lists its recent job runs, and expanding any run shows the full logs for that execution.

#### View a pipeline's job runs

1. Open the **Pipelines** view from the left navigation bar.
2. Find the pipeline you want to inspect. Each pipeline is shown as a card with its name and latest run status.
3. Click the chevron (⌄) on the pipeline card to expand it and reveal its recent job runs.

#### View logs for a specific run

1. With the pipeline card expanded, locate the job run you want to inspect.
2. Click on that run to open its logs.
3. Use the logs to see exactly what happened during that run — useful for spotting errors, warnings, or unexpected behaviour before reaching for a deeper diagnosis.

If a run failed and you want more than raw logs — for example, a plain language explanation of what went wrong and how to fix it — use Melty AI (below).

### Diagnosing pipelines with Melty AI

When a pipeline fails, Melty AI reads the failure and explains what went wrong in plain language, along with suggested steps to fix it.

#### Before you start

Melty AI runs on your own Claude API key, so there's a one-time setup step before you can use it.

1. Go to **Settings > Advanced Settings > Claude**.
2. Add your Claude API key.
3. If you don't have one yet, generate one from the [Anthropic Console](https://console.anthropic.com).

You only need to do this once. Once a key is added, Diagnose is available on any failing pipeline.

#### How to use Diagnose

**1. Find a failing pipeline** — Open the **Pipelines** view. Any pipeline whose latest run has failed shows a **Diagnose** button next to it.

**2. Click Diagnose** — If this is your first time using the feature, you'll see an introduction explaining what Melty AI does and what data it uses, with a prompt to add your Claude API key if you haven't already. Once a key is on file, clicking Diagnose goes straight to generating a diagnosis.

**3. Read the diagnosis** — Melty AI gathers the failure logs, recent run history, pipeline code, and pipeline configuration, and sends that context to Claude. The result appears in a popup with:

- A short title summarizing the failure
- A plain language explanation of what went wrong
- Suggested steps to resolve it

**4. Close the popup** — Click **Close** when you're done. Your diagnosis isn't lost — it's saved against that run, so you can come back to it later without generating it again.

#### Diagnosis caching

Once a diagnosis is generated for a failed run, it's cached in your workspace. Reopening that failure shows the cached diagnosis instead of generating a new one, so you're not spending API tokens asking the same question twice.

A new diagnosis is only generated when:

- You're viewing a failure for the first time, or
- The pipeline fails again on a subsequent run

Only the diagnosis itself is cached, not the raw logs, code, or context that was sent to Claude to produce it.

#### Data handling and privacy

Because Melty AI sends pipeline logs and code to Claude to generate a diagnosis, here's exactly what's sent, what's protected, and where it goes.

**What Melty AI looks at.** Four things, and only these four:

- Failure logs for the run that triggered the diagnosis
- Recent run history for that pipeline, so Claude can tell whether this is a new failure or a recurring one
- Pipeline code, the configuration hosted in your pipeline's git repository
- Pipeline metadata, such as which plugins and triggers are configured

Melty AI does not look at data from other pipelines, other workspaces, or anything outside what's needed to diagnose the specific failure you clicked into.

**What's removed before anything is sent.** Before any of the above leaves Meltano, it passes through an automatic redaction step. This uses URL and key-pattern scrubbing, combined with Meltano's secret-setting flags, to strip out:

- Credentials, tokens, and API keys that may appear in logs or configuration
- Connection strings and secrets referenced in pipeline code
- Any other values Meltano's redaction system is configured to treat as sensitive

This happens automatically and applies the same way everywhere a pipeline's logs are surfaced. There's no setting to turn it off.

**What Meltano stores, and what it doesn't.** Meltano stores the generated diagnosis in your workspace, so reopening a failure doesn't require regenerating it or spending tokens again. Meltano also records token usage for accounting purposes.

Meltano does not persist the raw context, logs, code, or configuration that was sent to Claude to produce a diagnosis. That data exists only for the duration of the request.

**Where the request goes.** Melty AI runs on your own Claude API key, so each request is made under your own Anthropic account rather than a shared Meltano-owned key. The redacted context is sent directly to Claude via Anthropic's API. Because the request is made under your account, Anthropic's handling of that data is governed by [Anthropic's privacy and data usage policies](https://www.anthropic.com/legal/privacy), not Meltano's.

**Your control over this.**

- Melty AI only runs when you click Diagnose. It never runs automatically on a failure.
- If you haven't added a Claude API key, no data is sent anywhere — you'll be prompted to add one first.
- You can remove your Claude API key at any time from **Settings > Advanced Settings > Claude**, which disables Melty AI until a new key is added.

#### Questions

If you have questions about this feature or want to report something that looks wrong in a diagnosis, contact Meltano support or reach out through your usual support channel.

---

## Log routing and monitoring

Stream your workspace pipeline logs to external monitoring platforms for real-time visibility and alerting.

### Datadog log streaming

Send workspace logs directly to Datadog for monitoring, alerting, and observability across your pipelines.

Requirements: a Datadog API key and an active Datadog account.

#### Setting up Datadog

1. Open **Workspace Settings** and scroll to the **External Logging Services** section.
2. Click **Add Credential** under the Datadog section.
3. Fill in the following details:
   - **API Key**: Your Datadog API key.
   - **Region**: Select the Datadog region that matches your account to ensure logs reach the correct data centre.
   - **Service Name** *(optional)*: Tag logs with a service name to filter them and build focused dashboards in Datadog.
4. Click **Save**: logs will begin streaming to Datadog immediately.

#### Managing your Datadog credentials

- **Pause streaming**: Click the **Active** toggle on your Datadog credentials card to switch it to **Paused**. Logs will stop streaming without removing your credentials.
- **Resume streaming**: Click the **Paused** toggle to switch back to **Active**. Log streaming resumes immediately.
- **Delete credentials**: Remove your Datadog credentials at any time, for example when rotating API keys or switching regions. Re-add them to resume streaming.

#### How it works

Logs are shipped from the Logback layer directly to Datadog — no extra infrastructure required. Settings take effect at runtime, so you can adjust configuration without redeploying your workspace.

---

## Profile and security

Access all profile-level settings by clicking your profile icon in the top-right corner of the app.

Use this section to keep your credentials secure, connect to the API for custom workflows, or manage your account plan and billing.

### Change your password

Use this when you want to rotate your credentials or regain access after forgetting your password.

1. Click your profile icon in the top-right corner.
2. Select **Change Password** from the dropdown.
3. A confirmation message will appear — a password reset email has been sent to your registered address.
4. Open the email from Support with the subject "Change password - Password Change Request".
5. Click the link in the email to open the reset form.
6. Enter and confirm your new password.
7. Submit to complete the change.

Note: The reset link in the email is single-use and expires after a short period. If it no longer works, repeat the steps above to request a new one.

### Access your API keys

Use this when you're building integrations, connecting external tools, or authenticating programmatic access to Meltano Cloud.

1. Click your profile icon in the top-right corner.
2. Select **API Keys** from the dropdown.
3. Your Developer Token and Client ID are displayed on the page.
4. Click the copy icon next to either value to copy it to your clipboard.

Note: Keep your Developer Token private — treat it like a password. Do not share it or commit it to version control.

### Manage your account

Use this to update your plan, billing details, or account-level preferences.

1. Click your profile icon in the top-right corner.
2. Select **Manage Account** from the dropdown.
3. You'll be redirected to the Matatika account page where you can manage your subscription and settings.

### Log out

Use this when you're done with your session or switching between accounts.

1. Click your profile icon in the top-right corner.
2. Select **Log Out** from the dropdown.
3. You'll be signed out and redirected to the login page.
