#!/usr/bin/env bash
# Local Postgres warehouse lifecycle (no Docker required).
#
# Uses the PostgreSQL 16 server binaries shipped by the `pgserver` pip package,
# running as your own user. Data lives in <project>/.pgdata.
#
# Usage: ./orchestrate/warehouse/pg.sh {start|stop|restart|status|psql|logs}
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PGDATA="$PROJECT_ROOT/.pgdata"
PGHOME="$HOME/.local/share/pg-warehouse"
PGBIN="$(echo "$PGHOME"/venv/lib/python3*/site-packages/pgserver/pginstall/bin)"

# Overridable so a second cluster can run alongside the first.
PGPORT_="${WAREHOUSE_PORT:-5432}"
PGDB="${WAREHOUSE_DB:-warehouse}"
PGUSER_="${WAREHOUSE_USER:-meltano}"
PGPASS="${WAREHOUSE_PASSWORD:-meltano}"

if [[ ! -x "$PGBIN/pg_ctl" ]]; then
  echo "Postgres binaries not found at $PGBIN" >&2
  echo "Run: uv venv $PGHOME/venv --python 3.12 && VIRTUAL_ENV=$PGHOME/venv uv pip install pgserver" >&2
  exit 1
fi

case "${1:-status}" in
  start)
    if [[ ! -d "$PGDATA" ]]; then
      echo "No cluster at $PGDATA — initialising..."
      pwfile="$(mktemp)"; printf '%s' "$PGPASS" > "$pwfile"
      "$PGBIN/initdb" -D "$PGDATA" -U postgres --auth-local=trust \
        --auth-host=scram-sha-256 --pwfile="$pwfile" -E UTF8 --locale=C >/dev/null
      rm -f "$pwfile"
      cat >> "$PGDATA/postgresql.conf" <<CONF

# --- meltano warehouse settings ---
listen_addresses = 'localhost'
port = $PGPORT_
unix_socket_directories = '/tmp'
CONF
      "$PGBIN/pg_ctl" -D "$PGDATA" -l "$PGDATA/server.log" start
      until "$PGBIN/pg_isready" -h localhost -p "$PGPORT_" >/dev/null 2>&1; do sleep 1; done
      PGHOST=/tmp PGPORT="$PGPORT_" "$PGBIN/psql" -U postgres -d postgres -v ON_ERROR_STOP=1 <<SQL
CREATE ROLE $PGUSER_ WITH LOGIN PASSWORD '$PGPASS' CREATEDB;
CREATE DATABASE $PGDB OWNER $PGUSER_;
SQL
      PGHOST=/tmp PGPORT="$PGPORT_" "$PGBIN/psql" -U postgres -d "$PGDB" -v ON_ERROR_STOP=1 \
        -c "CREATE SCHEMA IF NOT EXISTS raw AUTHORIZATION $PGUSER_;"
      echo "Cluster initialised: postgresql://$PGUSER_@localhost:$PGPORT_/$PGDB"
    else
      "$PGBIN/pg_ctl" -D "$PGDATA" -l "$PGDATA/server.log" start
      until "$PGBIN/pg_isready" -h localhost -p "$PGPORT_" >/dev/null 2>&1; do sleep 1; done
    fi
    "$PGBIN/pg_isready" -h localhost -p "$PGPORT_"
    ;;
  stop)    "$PGBIN/pg_ctl" -D "$PGDATA" stop -m fast ;;
  restart) "$0" stop || true; "$0" start ;;
  status)  "$PGBIN/pg_ctl" -D "$PGDATA" status || true
           "$PGBIN/pg_isready" -h localhost -p "$PGPORT_" || true ;;
  psql)    shift || true
           PGPASSWORD="$PGPASS" "$PGBIN/psql" -h localhost -p "$PGPORT_" -U "$PGUSER_" -d "$PGDB" "$@" ;;
  logs)    tail -n 100 -f "$PGDATA/server.log" ;;
  *) echo "Usage: $0 {start|stop|restart|status|psql|logs}" >&2; exit 1 ;;
esac
