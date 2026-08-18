# Meltano Cloud Overview

Meltano Cloud is the fully managed, hosted edition of Meltano built by Matatika — the fastest way to run production ELT pipelines without managing infrastructure.

## Why teams use Meltano Cloud

Sign up, connect a Git repo, define your pipelines, and Meltano handles the rest: deployments, scheduling, credentials, and monitoring are all managed for you.

Features covered under Meltano Cloud are not available in the Community or Open (self-hosted, open-source) editions of Meltano.

## Why companies choose Meltano Cloud

- **No infrastructure to manage**: workspaces, deployments, and scheduling are handled for you; you connect a repo and Meltano runs it.
- **Git-backed by design**: every workspace is backed by a GitHub repository, so your pipeline config stays version-controlled and auditable.
- **Isolated by team or project**: each workspace has its own pipelines, data store connection, members, and credentials.
- **Credentials handled safely**: deployment keys and credentials live in Settings inside your workspace.

## Get started in 6 steps

1. **Get in touch**: Create your Meltano Cloud account at [meltano.com/contact](https://meltano.com/contact). You can sign in with GitHub or Google.

2. **Create a workspace**: A workspace is an isolated environment for your team. Name it after your organization or project, then invite teammates from the Members tab.

3. **Connect a Git repository**: Link the GitHub repo that contains (or will contain) your `meltano.yml`. Meltano Cloud reads your pipeline definitions directly from your repo on every run.

4. **Add credentials**: Set your deployment keys and credentials in Settings.

5. **Install a plugin and create a pipeline**: In the Lab, find and install the extractor for your data source, then click **+ Pipeline** next to it. Fill in the required connection settings and set a schedule (or leave it manual for now).

6. **Trigger a pipeline run**: Save your pipeline and wait for the config job to finish (1-2 minutes). This commits your pipeline to the workspace repo. Once it completes, trigger a run from the Cloud UI or with `meltano cloud run`, and watch live logs stream directly in the interface. Don't trigger a run while the config job is still in progress — wait for it to finish first. Once your first run succeeds, you can set a recurring schedule, stream logs to DataDog, and add alerting, all from the Cloud UI.

## Getting help

If you cannot find an answer to your question, there's an active [Meltano Slack Community](https://meltano.com/slack) to help you out.
