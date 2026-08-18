# Data Stores

How to connect, configure, and manage the data warehouses that power a Meltano Cloud workspace, plus store-specific security and connection guides for Snowflake, Microsoft SQL Server, ClickHouse, and MotherDuck.

## Connecting a store — overview

Navigate to **Workspace → Stores** from the left navigation bar to view, add, and manage the data stores connected to your workspace.

- Every Meltano workspace comes with a default **PostgreSQL** data store called **Warehouse**, managed by Meltano out of the box.
- The Warehouse data store is automatically set as both `MANAGED` and `DEFAULT` when your workspace is created.
- Changing the default data store affects where **data imports load data into** and where **datasets query data from**.

### Store labels

**`MANAGED`**
- Only the default **Warehouse** data store carries the `MANAGED` label.
- A `MANAGED` store cannot be edited or deleted.
- Meltano provides this store so you can run and test pipelines immediately, and to store pipeline state and bookmarks for future runs.

**`DEFAULT`**
- The `DEFAULT` store is the one your workspace uses automatically in pipelines and as the data source for datasets.
- You can create additional stores and set any of them as `DEFAULT` if needed.
- Non-default stores can still be used in specific pipelines — they just won't be selected automatically.
- Note: The default store cannot be deleted until another store is set as the default.

### Supported data stores

Meltano supports the following data stores for powering your workspace:

- **PostgreSQL**
- **Snowflake**
- **BigQuery**
- **Microsoft SQL Server**
- **ClickHouse**
- **MotherDuck**

Custom data stores (those not natively provided by Meltano) support loading data via data import runs, but do not support querying via datasets. If a custom store is set as default, data will load normally but all datasets will appear empty.

### Adding a new data store

Prerequisites:
- Owner or admin access to a Meltano workspace.
- Credentials for a supported database (PostgreSQL, Snowflake, BigQuery, or MS SQL).

Steps:

1. Go to **Workspace → Stores** in the left navigation bar.
2. Click **Add** on the Stores page.
3. On the next screen, select your preferred data store and click **Install**, then click **Add**.
4. Enter the required credentials and connection properties for the selected store.
5. Click **Save**, then navigate back to the **Stores** page.

### Setting a data store as default

1. On the **Stores** page, locate the data store you want to set as default.
2. Click the three-dot menu (⋮) on that store's card.
3. Select **Make Default** from the dropdown.

What changes after setting a new default:
- All future data imports will load into the new default store (unless a specific store is chosen manually).
- All datasets will query from the new default store.
- The previous Meltano-managed PostgreSQL database is not affected — no data is moved or deleted — and can be made the default again at any time.

### Editing a data store

1. Click the three-dot menu (⋮) on the store card.
2. Select **Edit** to update the store's credentials or connection properties.
3. Save your changes.

`MANAGED` stores cannot be edited.

### Deleting a data store

1. Click the three-dot menu (⋮) on the store card.
2. Select **Delete** from the dropdown.
3. A confirmation modal will appear with the message "This action cannot be undone."
4. Click **Delete** to confirm, or **Cancel** to return to the Stores page.

A store marked as `DEFAULT` cannot be deleted. Set another store as the default first before attempting to delete it.

---

### Snowflake

Meltano regularly shares best practices for secure and efficient analytics engineering. The guides below cover common Snowflake security configurations: whitelisting IP ranges and setting up key pair authentication.

#### Whitelist IP ranges

Whitelisting IP addresses adds an extra layer of security to your Snowflake data warehouse by only allowing trusted clients to connect.

This approach blocks all internet traffic except approved IP addresses, such as:

- Developers
- Data ingestion services like Meltano
- Other trusted applications

The Meltano platform has multi cloud resilience within the United Kingdom and connects from the following IP addresses:

```text
51.137.148.226
35.189.66.90
35.177.0.220
```

**Create network rules:**

```sql
CREATE NETWORK RULE block_all_public_access
  MODE = INGRESS
  TYPE = IPV4
  VALUE_LIST = ('0.0.0.0/0');

CREATE NETWORK RULE allow_meltano_access_rule
  MODE = INGRESS
  TYPE = IPV4
  VALUE_LIST = ('51.137.148.226', '35.189.66.90', '35.177.0.220');

CREATE NETWORK POLICY secure_data_policy
  ALLOWED_NETWORK_RULE_LIST = ('allow_meltano_access_rule')
  BLOCKED_NETWORK_RULE_LIST = ('block_all_public_access');
```

For complete details, see the Snowflake Network Policy documentation.

**Apply the policy** — to the entire account:

```sql
ALTER ACCOUNT SET NETWORK_POLICY = secure_data_policy;
```

Or apply it to a specific user:

```sql
ALTER USER joe SET NETWORK_POLICY = secure_data_policy;
```

#### Key pair authentication

Two-factor authentication (2FA) is one of the simplest ways to secure Snowflake accounts for human users.

For services and automated systems, key-pair authentication provides a more secure alternative to passwords. Snowflake is also phasing out basic password-only authentication, making key-pair authentication the recommended approach for unattended services such as data ingestion pipelines.

For full details, see the [Snowflake Key-pair authentication documentation](https://docs.snowflake.com/en/user-guide/key-pair-auth).

**Step 1: Generate a private key**

```bash
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -v1 PBE-SHA1-3DES -out rsa_key.p8
```

This creates an encrypted private key.

**Step 2: Generate a public key**

```bash
openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub
```

**Step 3: Securely store your keys**

Treat the private key (`rsa_key.p8`) like a password:

- Do not share it
- Do not commit it to source control
- Store it securely in a password vault such as 1Password

Store the following securely: `rsa_key.p8` (private key), `rsa_key.pub` (public key), encryption password.

**Step 4: Assign the public key to a Snowflake user**

```sql
ALTER USER example_user SET RSA_PUBLIC_KEY='MIIBIjANBgkqh...';
```

Only the user owner or users with the `SECURITYADMIN` role (or higher) can modify user settings. Do not include the public key delimiters in the SQL statement.

**Step 5: Verify the public key fingerprint**

Retrieve the fingerprint:

```sql
DESC USER example_user;

SELECT SUBSTR(
  (
    SELECT "value"
    FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()))
    WHERE "property" = 'RSA_PUBLIC_KEY_FP'
  ),
  LEN('SHA256:') + 1
);
```

Example output:

```text
Azk1Pq...
```

Generate a fingerprint from the public key:

```bash
openssl rsa -pubin -in rsa_key.pub -outform DER \
| openssl dgst -sha256 -binary \
| openssl enc -base64
```

Example output:

```text
writing RSA key
Azk1Pq...
```

If both outputs match, the public key has been configured correctly.

Restricting access to your Snowflake account and reducing reliance on passwords helps protect against attacks such as phishing, brute force attacks, and credential stuffing.

---

### Microsoft SQL Server

Guides for common Microsoft SQL Server configurations: whitelisting IP ranges and setting up Azure Blob Storage staging.

#### Whitelist IP ranges

Whitelisting IP addresses adds an extra layer of security to your SQL Server by only allowing trusted clients to connect.

This approach blocks all internet traffic except approved IP addresses, such as:

- Developers
- Data ingestion services like Meltano
- Other trusted applications

The Meltano platform is hosted in an Azure data center within the United Kingdom and connects from the following IP addresses:

```text
51.137.148.226
35.189.66.90
35.177.0.220
```

**Create a firewall rule** — for Azure SQL Database, add a server-level firewall rule allowing these addresses:

```sql
EXECUTE sp_set_firewall_rule
    @name = N'AllowMeltano',
    @start_ip_address = '51.137.148.226',
    @end_ip_address = '51.137.148.226';
```

```sql
EXECUTE sp_set_firewall_rule
    @name = N'AllowMeltano',
    @start_ip_address = '35.189.66.90',
    @end_ip_address = '35.189.66.90';
```

```sql
EXECUTE sp_set_firewall_rule
    @name = N'AllowMeltano',
    @start_ip_address = '35.177.0.220',
    @end_ip_address = '35.177.0.220';
```

Or using the `az` CLI:

```bash
az sql server firewall-rule create \
  --resource-group <rg> \
  --server <server> \
  --name AllowMeltano \
  --start-ip-address 51.137.148.226 \
  --end-ip-address 51.137.148.226
```

```bash
az sql server firewall-rule create \
  --resource-group <rg> \
  --server <server> \
  --name AllowMeltano \
  --start-ip-address 35.189.66.90 \
  --end-ip-address 35.189.66.90
```

```bash
az sql server firewall-rule create \
  --resource-group <rg> \
  --server <server> \
  --name AllowMeltano \
  --start-ip-address 35.177.0.220 \
  --end-ip-address 35.177.0.220
```

For complete details, see the [Azure SQL Database firewall documentation](https://learn.microsoft.com/en-us/azure/azure-sql/database/firewall-configure).

#### Azure Blob Storage staging

By default, [`target-mssql`](https://github.com/MeltanoLabs/target-mssql) loads records row by row. For large data volumes you can enable Azure Blob Storage staging, which is significantly faster.

Staging streamlines data loading through a three-phase process:

1. Each batch serializes to JSON on disk.
2. The file uploads to Azure Blob Storage.
3. SQL Server retrieves it via `OPENROWSET(BULK …, DATA_SOURCE = …)` and runs either `INSERT` (append-only) or `MERGE` (upsert).

The blob is removed following successful completion.

**Prerequisites — Azure Blob Storage**

Establish a Storage Account (general-purpose v2), a container such as `mssql-stage`, and a SAS token limited to that container with the minimum permissions: Read, Write, Create, and Delete on the Object resource type.

Using the `az` CLI:

```bash
KEY=$(az storage account keys list \
  --account-name <storage_account> \
  --query "[0].value" \
  --output tsv)

SAS=$(az storage container generate-sas \
  --account-name <storage_account> \
  --name mssql-stage \
  --permissions rwdc \
  --expiry 2027-01-01T00:00:00Z \
  --https-only \
  --account-key "$KEY" \
  --output tsv)
```

**SQL Server one-time DBA setup**

The target does not create the credential or external data source — a DBA must configure them once before the initial run.

Step 1: Create a database master key (required once per database):

```sql
IF NOT EXISTS (SELECT 1 FROM sys.symmetric_keys WHERE name = '##MS_DatabaseMasterKey##')
    CREATE MASTER KEY ENCRYPTION BY PASSWORD = '<strong-password>';
```

Step 2: Create a database scoped credential. Pick one of two options:

*Option A: SAS token* — straightforward to implement; the token has an expiration and needs periodic renewal.

```sql
/*
-- To recreate the object, first run:
DROP EXTERNAL DATA SOURCE target_mssql_stage;
DROP DATABASE SCOPED CREDENTIAL [target_mssql_credential];
*/

CREATE DATABASE SCOPED CREDENTIAL [target_mssql_credential]
    WITH IDENTITY = N'SHARED ACCESS SIGNATURE',
         SECRET   = N'<sas-token-without-leading-?>';
```

To renew the token later:

```sql
ALTER DATABASE SCOPED CREDENTIAL [target_mssql_credential]
    WITH IDENTITY = N'SHARED ACCESS SIGNATURE',
         SECRET   = N'<new-sas-token-without-leading-?>';
```

*Option B: Managed Identity* — no credentials requiring rotation. Requires an Azure SQL Server (not on-premises) with a system-assigned managed identity enabled.

Prerequisites (Azure portal or CLI):

1. Activate the system-assigned managed identity on the Azure SQL Server:
   - Portal: **Azure SQL Server → Security → Identity → System assigned managed identity → On**
   - CLI: `az sql server update --name <server> --resource-group <rg> --assign-identity`

2. Assign the SQL Server's managed identity the **Storage Blob Data Owner** (or **Storage Blob Data Reader**) role on the container:
   - Portal: **Storage account → Access Control (IAM) → + Add → Add role assignment**, then select the "Storage Blob Data Owner" role for the SQL Server managed identity.
   - CLI:

     ```bash
     PRINCIPAL_ID=$(az sql server show \
       --name <server> \
       --resource-group <rg> \
       --query "identity.principalId" \
       --output tsv)

     az role assignment create \
       --assignee "$PRINCIPAL_ID" \
       --role "Storage Blob Data Owner" \
       --scope "/subscriptions/<subscription-id>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/<account_name>/blobServices/default/containers/<container>"
     ```

SQL:

```sql
/*
-- To recreate the object, first run:
DROP EXTERNAL DATA SOURCE target_mssql_stage;
DROP DATABASE SCOPED CREDENTIAL [target_mssql_credential];
*/

CREATE DATABASE SCOPED CREDENTIAL [target_mssql_credential]
    WITH IDENTITY = N'MANAGED IDENTITY';
```

Step 3: Create the external data source, pointing it at the container:

```sql
CREATE EXTERNAL DATA SOURCE [target_mssql_stage]
    WITH (
        TYPE       = BLOB_STORAGE,
        LOCATION   = N'https://<account_name>.blob.core.windows.net/<container>',
        CREDENTIAL = [target_mssql_credential]
    );
```

Step 4: Grant the target user permissions:

```sql
-- Database-level (run in the target database)
ALTER ROLE db_datareader ADD MEMBER [<db-user>];      -- SELECT on all tables
ALTER ROLE db_datawriter ADD MEMBER [<db-user>];      -- INSERT, UPDATE, DELETE on all tables
GRANT CREATE TABLE TO [<db-user>];                    -- create target tables for new streams
GRANT ALTER ANY EXTERNAL DATA SOURCE TO [<db-user>];  -- create the EXTERNAL DATA SOURCE on first run

-- Server-level (run as sysadmin in master)
GRANT ADMINISTER DATABASE BULK OPERATIONS TO [<db-user>];   -- execute OPENROWSET(BULK …)
```

On-premises SQL Server 2017+ also requires Ad Hoc Distributed Queries:

```sql
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC sp_configure 'Ad Hoc Distributed Queries', 1; RECONFIGURE;
```

Azure SQL Database has this enabled automatically.

To remove the objects if necessary:

```sql
DROP EXTERNAL DATA SOURCE [target_mssql_stage];
DROP DATABASE SCOPED CREDENTIAL [target_mssql_credential];
```

**Configuration**

Add the `azure_blob_storage` settings to your `target-mssql` configuration:

```json
{
  "azure_blob_storage": {
    "account_name": "mystorageaccount",
    "sas_token": "sv=2023-11-03&sr=c&sp=rwdc&se=2027-01-01T00:00:00Z&sig=...",
    "container": "mssql-stage",
    "path_prefix": "target-mssql"
  }
}
```

| Option | Required | Default | Description |
|---|---|---|---|
| `account_name` | Yes | | Azure Storage account name |
| `sas_token` | Yes | | SAS token (without a leading `?`) or storage account access key |
| `container` | Yes | | Blob container used as the staging area |
| `path_prefix` | No | `target-mssql` | Virtual directory prefix inside the container |

Despite its name, `sas_token` accepts either a SAS token or the storage account's access key — the value is passed directly to the Azure Blob Storage client as its credential.

Choosing between the two:

| Credential | Benefits | Drawbacks |
|---|---|---|
| **SAS token** | Can be scoped to a single container with only the permissions it needs (`rwdc`), and has an expiry — limiting the blast radius if leaked. | Expires, so it must be rotated before the expiry date or uploads will start failing. |
| **Storage account key** | Never expires, so there is nothing to rotate on a schedule. | Grants full read/write/delete access to *every* container in the account; cannot be scoped or time-limited, so a leak compromises the whole storage account. |

We recommend a SAS token, scoped as narrowly as possible. The `az storage container generate-sas` command above produces a *service SAS* limited to one container — the tightest scope for this use case. (SAS tokens can also be account-wide; an *account SAS* spans the whole storage account and offers little advantage over the account key for staging.) Use an account key only when token rotation is impractical, and rotate it manually if it is ever exposed.

**Performance notes**

- Minimum SQL Server version: 2017 (14.x). Azure SQL Database and Azure SQL Managed Instance are fully supported.
- Batch size: use a larger `batch_size_rows` to distribute the overhead of per-batch blob communication (e.g. `"batch_size_rows": 50000`).
- Booleans: stored as `BIT` in the staged file, inserted into the target's `VARCHAR(1)` column as `0`/`1`.
- Complex types (objects, arrays): encoded to JSON strings, stored as `NVARCHAR(MAX)` — matching the non-staged approach.

Restricting network access to your SQL Server and avoiding long-lived credentials (for example, by using a Managed Identity for blob staging) helps protect against attacks such as phishing, brute force attacks, and credential stuffing.

---

### ClickHouse

This guide covers the security best practices and connection settings for using ClickHouse as a store with Meltano — whitelisting, authentication, connection settings and tuning the loader for OLAP workloads — and then walks through connecting ClickHouse as a **full data store** (loader, state backend and dbt transforms together).

#### Supported versions

- **ClickHouse server 22.8 or newer.** Earlier versions (e.g. 21.8) fail on the loader's default native bulk-insert path — the HTTP client sends `lz4` compression that older servers don't recognise. 22.8+ supports the full feature set the loader relies on (`ReplacingMergeTree` + `FINAL` + `OPTIMIZE`, `async_insert`).
- **ClickHouse Cloud** is supported over its HTTPS interface (port `8443`).

#### Whitelist IP ranges

Restricting inbound connections to trusted clients is the single most effective way to protect your ClickHouse instance. Only the following should be able to reach it:

- Your own data team and BI tools
- Your dbt/analytics runners
- Meltano

The Meltano platform has multi-cloud resilience within the United Kingdom and connects to your store from the following egress IP addresses:

```text
51.137.148.226
35.189.66.90
35.177.0.220
```

**ClickHouse Cloud**

In the ClickHouse Cloud console, open your service → **Settings** → **Security** → **IP Access List** and add an allowed entry:

```text
51.137.148.226/32   # Meltano
35.189.66.90/32     # Meltano
35.177.0.220/32     # Meltano
```

Ensure there is no `0.0.0.0/0` (Anywhere) entry in the IP Access List: if one already exists, remove it so that only specific IP addresses (including Meltano's) that you add explicitly can connect.

**Self-managed ClickHouse**

Restrict the service user to Meltano's IP in your users configuration (`users.xml` or a file under `users.d/`). The `import_runner` user referenced below is created in Authentication (below) — create it first, then apply this network restriction:

```xml
<clickhouse>
  <users>
    <import_runner>
      <networks>
        <ip>51.137.148.226/32</ip>
      </networks>
    </import_runner>
  </users>
</clickhouse>
```

See the [ClickHouse user settings documentation](https://clickhouse.com/docs/operations/settings/settings-users) for the full `<networks>` syntax.

#### Authentication

Create a dedicated service user for Meltano rather than reusing `default`. This lets you scope permissions and rotate the credential independently.

Step 1: Create the user and database. Run the following as an administrator. ClickHouse has no schema namespace distinct from the database — a database *is* the schema — so grants are scoped at the database level.

```sql
-- Dedicated load target database (this is also the "schema")
CREATE DATABASE IF NOT EXISTS meltano;

-- Service user
CREATE USER IF NOT EXISTS import_runner IDENTIFIED WITH sha256_password BY '<strong-password>';
```

Step 2: Grant permissions:

```sql
-- Permissions the loader needs to create and maintain target tables
GRANT SELECT, INSERT, ALTER, CREATE TABLE, DROP TABLE, OPTIMIZE
  ON meltano.* TO import_runner;
```

If you also use ClickHouse as your state backend (recommended — see "Set up ClickHouse as a full data store" below), the same user and grant already cover it, since the state table lives in `meltano.state`.

Step 3: Use TLS in production. For any store reachable over the public internet, connect over HTTPS/TLS. Set `secure: true` and use the TLS port `8443` (ClickHouse Cloud terminates TLS on `8443` by default). Keep `verify: true` so the server certificate is validated.

For full details on ClickHouse authentication options, see the [ClickHouse user settings documentation](https://clickhouse.com/docs/operations/settings/settings-users).

#### Configuration

Connect the store with the following settings — you'll enter them when creating the store in the platform (see Step 2 of the walkthrough below). The minimum required fields are `host`, `database`, and a password.

```json
{
  "host": "your-instance.clickhouse.cloud",
  "port": 8443,
  "driver": "http",
  "username": "import_runner",
  "password": "<strong-password>",
  "database": "meltano",
  "secure": true,
  "verify": true,
  "engine_type": "MergeTree",
  "load_method": "append-only"
}
```

| Option | Required | Default | Description |
|---|---|---|---|
| `host` | Yes | - | ClickHouse host. |
| `port` | No | `8123` | `8123` for the HTTP driver (`8443` when `secure`), or `9000` for the native driver. |
| `driver` | No | `http` | Client driver: `http` (bulk-insert over the HTTP interface), `native`, or `asynch`. |
| `username` | No | `default` | ClickHouse user. |
| `password` | Yes | - | ClickHouse password. |
| `database` | Yes | - | Target database. ClickHouse has no separate schema — the database *is* the schema. |
| `secure` | No | `false` | Connect over HTTPS/TLS. Enable for ClickHouse Cloud; set `port` to `8443`. |
| `verify` | No | `true` | Verify the server's TLS certificate when `secure` is enabled. |
| `engine_type` | No | `MergeTree` | Table engine. `MergeTree` for append-only; `ReplacingMergeTree` (with `optimize_after`) for upserts. `Replicated*` engines also require `table_path`, `replica_name`, `cluster_name`. |
| `load_method` | No | `upsert` | `upsert` deduplicates by primary key (ReplacingMergeTree + `optimize_after`); `append-only` writes all records; `overwrite` replaces all rows. |
| `optimize_after` | No | `false` | Run `OPTIMIZE TABLE` after each load. Required for `ReplacingMergeTree` upserts to collapse duplicates. |
| `order_by_keys` | No | stream key | `ORDER BY` key. For `ReplacingMergeTree` this is the dedup key. |
| `default_target_schema` | No | - | Overrides the target database. On ClickHouse the database is the schema, so prefer setting `database` directly. |
| `async_insert` | No | `false` | Server-side async inserts for the HTTP driver — coalesces small inserts to reduce part churn on high-volume ingestion. |
| `batch_size_rows` | No | `10000` | Rows per load batch. |
| `add_record_metadata` | No | `true` | Add `_sdc_*` metadata columns. Required for `activate-version` / hard-delete. |

An SSH tunnel (bastion host) is also supported via the `ssh_tunnel.*` settings if your ClickHouse instance is not directly reachable.

#### Set up ClickHouse as a full data store

ClickHouse is supported as a **full data store** in Meltano — meaning all pieces work together:

1. **Loader** — `target-clickhouse` writes your extracted data into ClickHouse.
2. **Transforms** — `dbt-clickhouse` runs your dbt models against ClickHouse.

**Prerequisites**

- A running ClickHouse instance (ClickHouse Cloud or self-managed), reachable from Meltano. See "Whitelist IP Ranges" above for network whitelisting and TLS.
- Admin access to create a user and database.
- The host, port and a service credential.

**Step 1: Create a service user and database**

Run as an administrator (see Authentication above for the least-privilege rationale). If you already created the user and database while following the Authentication section, you can skip straight to Step 2 — the statements below are safe to re-run either way:

```sql
CREATE DATABASE IF NOT EXISTS meltano;

CREATE USER IF NOT EXISTS import_runner IDENTIFIED WITH sha256_password BY '<strong-password>';

GRANT SELECT, INSERT, ALTER, CREATE TABLE, DROP TABLE, OPTIMIZE
  ON meltano.* TO import_runner;
```

The same user and database are reused for the loader, the state backend, and dbt.

**Step 2: Connect the ClickHouse store**

In the platform, create a new store and select **ClickHouse**. Fill in the connection settings for the instance from Step 1. Remember that on ClickHouse the database is the schema, so set `database` directly.

| Setting | Value |
|---|---|
| Host | `your-instance.clickhouse.cloud` |
| Port | `8443` (secure) / `8123` (plain HTTP) |
| Database | `meltano` |
| Username | `import_runner` |
| Password | *(your service password)* |
| Secure (TLS) | on |

See Configuration above for the full settings reference (drivers, SSH tunnel, TLS verification).

Choosing a load method:

- **Append-only** — writes every record. Best for immutable event/time-series streams and for incremental syncs, and avoids the cost of post-load `OPTIMIZE`. Recommended default.
- **Upsert** (default) — deduplicates by primary key using `ReplacingMergeTree` + `optimize_after`. Use only when you deliberately re-load overlapping keys. Set the store's `engine_type` to `ReplacingMergeTree`, `load_method` to `upsert`, and enable `optimize_after`.

Running open-source Meltano yourself? Configure the loader directly in `meltano.yml`:

```yaml
loaders:
  - name: target-clickhouse
    variant: meltanolabs
    config:
      host: your-instance.clickhouse.cloud
      port: 8443
      database: meltano
      username: import_runner
      secure: true
    # password supplied via TARGET_CLICKHOUSE_PASSWORD
```

For upsert, add `engine_type: ReplacingMergeTree`, `load_method: upsert`, and `optimize_after: true`.

**Step 3: State backend (handled automatically)**

This is what makes ClickHouse a *full* data store: pipeline state — the incremental bookmarks and full-table markers that let a sync resume instead of restarting — lives in ClickHouse itself, at parity with Postgres, Snowflake, BigQuery, and MSSQL.

On the platform you don't configure this. When you connect a ClickHouse store, the platform automatically derives the state backend from the same connection details and points Meltano at it — there's no separate URI, add-on, or credential to manage. State is written to `meltano.state` (a `ReplacingMergeTree(updated_at)` keyed by `state_id`, read with `FINAL` so the newest state always wins).

Running open-source Meltano yourself? Only if you run Meltano standalone (not on the platform) do you wire the state backend by hand. Install the add-on and point Meltano at a `clickhouse://` URI:

```bash
pip install "meltano-state-backend-clickhouse @ git+https://github.com/meltano/meltano-state-backend-clickhouse.git"
```

```yaml
state_backend:
  uri: clickhouse://user:password@host:8443/meltano
```

State is stored in `<schema>.<table>` (default `meltano.state`). Optional overrides: `state_backend.clickhouse.{host,port,database,user,password,secure,schema,table}`.

**Step 4: (Optional) Add dbt transforms**

To transform data in place, add dbt to your ClickHouse workspace. It uses `dbt-clickhouse` and pre-fills its connection from the store you connected in Step 2, so there's no separate profile to manage. (Standalone Meltano users add the `dbt-clickhouse` transformer and a profile pointing at the same instance and database.)

**Step 5: Verify**

Run a pipeline into your ClickHouse store from the workspace, then confirm data and state landed:

```sql
-- data
SELECT count() FROM meltano.<your_stream>;

-- state (written automatically by the state backend)
SELECT state_id, updated_at FROM meltano.state FINAL ORDER BY updated_at DESC LIMIT 5;
```

A second run of the same pipeline should resume from saved state (incremental) rather than reloading from scratch.

Running open-source Meltano yourself?

```bash
meltano run <your-extractor> target-clickhouse
```

#### Troubleshooting

- **`Table X.Y does not exist. Maybe you meant Z.Y?`** — you set both `database` and `default_target_schema` to different values. On ClickHouse the database is the schema; set `database` and leave `default_target_schema` unset.
- **Slow loads with `upsert`** — `optimize_after` runs `OPTIMIZE TABLE` (a full partition rewrite) after every load. Switch to `append-only` unless you need key-level dedup.
- **Duplicate rows visible between runs** — expected with `ReplacingMergeTree` until a merge/`OPTIMIZE` runs; enable `optimize_after` or query with `FINAL`.
- **Connection refused / timeout** — confirm Meltano's egress IP (`51.137.148.226`) is on your IP allow-list and that you're using the correct port (`8443` secure, `8123` plain HTTP, `9000` native).

#### Performance notes

- Prefer `append-only` unless you re-load overlapping keys. ClickHouse has no native row-level update; `upsert` is emulated with `ReplacingMergeTree` + `OPTIMIZE TABLE`, which rewrites whole partitions on every load. On large tables that cost can dominate the load. Only enable `upsert` when you deliberately re-ingest the same keys and want deduplication.
- `optimize_after` dedup is eventual. Without `OPTIMIZE`/`FINAL`, queries may briefly see duplicate rows between loads. `optimize_after: true` forces the collapse at the end of each run.
- Use `async_insert` for high-frequency, small-batch streams to reduce part churn.
- Native driver (port 9000) can be faster for very large loads; the HTTP driver (8123/8443) is the safe, firewall-friendly default.

Following this guide mitigates the most common threats to an internet-reachable analytics store: unauthorized network access (closed by the IP allow-list), credential compromise/lateral movement (limited by a dedicated, least-privilege service user scoped to a single database), and traffic interception (prevented by TLS with `secure: true`, `verify: true`).

---

### MotherDuck

#### Create a new database

To create a new database in MotherDuck, follow these steps:

1. Go to https://app.motherduck.com/home and log in to your MotherDuck account if you're not already logged in.
2. Look for the "Attached databases" section in the left sidebar.
3. Click on the + ("Add database") button.
4. Enter a name (e.g. `meltano`) for your database and click "Create database".
5. Copy the name of your database.

#### Create an access token

To create an access token for your MotherDuck database, follow these steps:

1. Go to https://app.motherduck.com/settings/tokens and log in to your MotherDuck account if you're not already logged in.
2. Click "Create token".
3. Enter a name and optional expiration date for your token and click "Create".
4. Copy the token and store it securely.

#### Configure Meltano

To configure your Meltano Workspace to use your MotherDuck database, follow these steps:

1. Add a new store to your Meltano Workspace using the `motherduck` store type.
2. Use `md:<your-database>` as the connection string, replacing `<your-database>` with the name of your database.
3. Paste in the access token you copied from the MotherDuck settings page.
