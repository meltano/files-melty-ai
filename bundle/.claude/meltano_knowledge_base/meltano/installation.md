# In-depth Installation

Detailed installation instructions for Meltano covering local installation (pipx/uv) on Linux, macOS, and Windows, plus Docker-based installation and upgrading.

> This is the in-depth installation guide. It may overlap with a simpler quick-start install doc elsewhere in this knowledge base — that's expected; this version covers requirements, troubleshooting, and edge cases in more depth.

## Local Installation

Install Meltano locally so you can use it on the command line.

> Windows is not fully supported yet, so some features like the ELT command may not work. See the GitHub "Windows" label for more information. If you'd like all of Meltano's features to work, install Meltano inside the Windows Subsystem for Linux (WSL), or try installing Meltano on Docker instead.

### Requirements

#### Python

Check that you have a supported Python version installed:

```shell
python --version
```

Currently Python 3.10, 3.11, 3.12, and 3.13 are supported. Not all plugins support these versions, so you might need to specify a different version for a given plugin (see the `python` setting reference).

#### Install pipx

`pip` is a package installer that comes automatically with Python 3+. `pipx` is a wrapper around `pip` which cleanly installs executable Python tools (such as Meltano) into their own virtual environments.

**Unix:**

```bash
# install pipx and ensure it is on the path
python3 -m pip install --user pipx
python3 -m pipx ensurepath
# Be sure pipx is available on your path
source ~/.bashrc
```

**Windows:**

```powershell
# install pipx and ensure it is on the path
python3 -m pip install --user pipx
python3 -m pipx ensurepath
# Be sure pipx is available on your path
RefreshEnv
```

> **Why use pipx and virtual environments?** Your local environment may use a different version of Python or other dependencies that are difficult to manage. The pipx installer automatically creates a virtual environment and provides a "clean" isolated space without version conflicts or other compatibility issues.

### Install Meltano

With pipx installed, run:

```bash
pipx install meltano
```

Check success:

```bash
meltano --version
```

### Install Git

Many Meltano plugins require Git. Check if it's installed:

```shell
git --version
```

If not installed, download it from the Git website.

### Optional Components

Some components of Meltano are optional and not installed by default — see "Installing Optional Components" in `deployment-and-operations.md` for details (extras like `postgres`, `mssql`, `s3`, `gcs`, `azure`).

### Next Steps

Once installed, continue setting up your project by following the Getting Started guide (see `data-pipelines.md`'s Complete ELT Walkthrough section).

## uv

`uv` is a Python package and project manager, written in Rust. It makes it easy to install a Python-based tool like Meltano in an isolated virtual environment.

```shell
uv tool install meltano
```

### Specifying a Python Version

```shell
uv tool install --python 3.13 meltano
```

This downloads the requested Python version (if not already installed) and installs Meltano in a virtual environment using that version.

## Docker

Docker is an alternative installation option to using a virtual environment to run Meltano. Install Docker onto your computer and have it running when executing the commands below.

### Using Pre-built Docker Images

Meltano maintains the `meltano/meltano` Docker image on Docker Hub, which comes with Python and Meltano pre-installed.

To get the latest version, pull the `latest` tag. Images for specific versions are tagged `v<X.Y.Z>`, e.g. `v3.5.4`.

By default, these images come with a Python version chosen for a balance of stability and compatibility (currently Python 3.10). To use a different version, add a `-python<X.Y>` suffix to the image tag, e.g. `latest-python3.11` and `v3.5.4-python3.11`.

```bash
# download or update to the latest version
docker pull meltano/meltano

# Or choose a specific version of Meltano and/or Python:
# docker pull meltano/meltano:v3.5.4
# docker pull meltano/meltano:latest-python3.11
# docker pull meltano/meltano:v3.5.4-python3.12

# check the currently installed version
docker run meltano/meltano --version
```

> See `deployment-and-operations.md` for details on Full vs Slim image variants and customizing the base image.

### Initialize Your Project

With Docker installed and the pre-built image pulled, use Meltano as you would locally, but with slightly different command line syntax:

```bash
cd /your/projects/directory

docker run -v "$(pwd)":/projects \
             -w /projects \
             meltano/meltano init yourprojectname
```

Then `cd` into your new project:

```bash
cd yourprojectname
```

Wherever you're asked to run the `meltano` command, run it through `docker run` as in the snippet above.

## Troubleshooting Installation

If you're having installation or deployment problems, check the Meltano issue tracker or the Meltano Slack workspace for help (see `troubleshooting-and-debugging.md` for general debugging techniques).

## Upgrading Meltano Version

New versions of Meltano are released every week. Follow along on the Meltano blog, or check the CHANGELOG on GitHub.

### Using the command line

Update Meltano to the latest version by running the following from inside a Meltano project:

```
meltano upgrade
```
