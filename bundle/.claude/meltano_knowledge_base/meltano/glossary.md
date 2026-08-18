# Glossary

A glossary of terms used in the Meltano documentation.

## Bookmarks

In a Singer extract-load pipeline, "bookmark" refers to the tracking artifact for a single stream. The state for any given tap likely contains many bookmarks, generally one per stream.

## CI/CD

CI/CD is a method to frequently deliver apps to customers by introducing automation into the stages of app development. (Learn more: https://www.redhat.com/en/topics/devops/what-is-ci-cd)

## DAG

DAG means Directed Acyclic Graph. Within data workflows, any sequence of linked tasks can be represented as a DAG. In dbt, this is done explicitly via the `ref` function.

## DataOps

DataOps brings the benefits of DevOps best practices to the data lifecycle. (Learn more: https://meltano.com/dataops/)

## ELT

ELT means Extract, Load, Transform — a method of data replication and transformation used to perform data integration at any scale. The purpose of ELT is to extract specific data (e.g. customer information, billing records) from its source and deliver it to its end point in the fastest, most reliable way possible. (Learn more: https://meltano.com/meltano-elt/)

## .env File

.env (pronounced "dot ehnv") files configure environment variables within an application. Useful for passing credentials and secrets to an app without checking passwords or keys into version control.

## Docker

Docker packages software into distributable/reproducible units called containers, containing most of what the software needs to run: libraries, system tools, code, and runtime. (Learn more: https://www.docker.com/)

## Docker Image

A Docker image contains application code, libraries, tools, dependencies, and other files needed to run an application. (Learn more: https://docs.docker.com/engine/reference/commandline/image/)

## Docker Container

A Docker container image is a lightweight, standalone, executable package of software including everything needed to run an application: code, runtime, system tools, system libraries, and settings. (Learn more: https://www.docker.com/resources/what-container/)

## Orchestration

Orchestration refers to the sequencing and running of tasks. Orchestrators run tasks at specified times and handle advanced features like retries. (Learn more: https://docs.meltano.com/guide/orchestration)

## Python Virtual Environment

A virtual environment is a Python environment such that the Python interpreter, libraries, and scripts installed into it are isolated from those installed in other virtual environments, and (by default) from any libraries installed in the "system" Python installed as part of the operating system. (Learn more: https://docs.python.org/3/library/venv.html)

## Singer

An open source specification for sending and receiving data. Unlike other similar standards, the Singer specification handles incremental use cases and is optimized for data replication use cases like those in ELT and data engineering workloads. (Learn more: https://hub.meltano.com/singer/spec)

## State

In Singer extract-load pipelines, "state" refers to progress trackers and artifacts enabling incremental replication. The state for a tap is a JSON object containing the set of bookmarks tracking the resume-point for all streams being replicated.

## Streams

In the Singer ecosystem, a stream typically represents a table, API endpoint, or discrete set of data. (Learn more: https://hub.meltano.com/singer/spec)

## Stream Map

In the Singer ecosystem, a stream map is an inline transformation applied to data on the fly before it arrives at a target. (Learn more: https://sdk.meltano.com/en/latest/stream_maps.html)

## Tap

In Singer extract-load pipelines, "tap" is synonymous with extractor — the plugin defining how data should be read from the source system.

## Target

In Singer extract-load pipelines, "target" is synonymous with loader — the plugin defining how data should be written to the destination.

## Transformation

Data transformation in a modern DataOps platform is a reproducible data shaping process that does not modify source data. It occurs after EL (extract-load) operations, shaping data into more usable datasets according to the business logic and use cases most valuable to the audience.
