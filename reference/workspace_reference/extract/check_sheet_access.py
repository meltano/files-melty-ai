#!/usr/bin/env python3
"""Verify the configured Google Sheet is readable anonymously.

tap-spreadsheets-anywhere sends no credentials on HTTPS requests, so the sheet must
stay shared as "Anyone with the link". Run this before `meltano run` to get a clear
answer instead of a 401 buried in tap logs.

    python3 extract/check_sheet_access.py

Also confirms every ${VAR} the config references is actually set in .env -- Meltano
expands an unset variable to an empty string without complaining.
"""
from __future__ import annotations

import csv
import io
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MELTANO_YML = PROJECT_ROOT / "meltano.yml"
DOTENV = PROJECT_ROOT / ".env"

VAR_PATTERN = re.compile(r"\$\{(\w+)\}|\$(\w+)")


def load_dotenv() -> dict[str, str]:
    """Read .env without adding a dependency. Real environment wins."""
    values: dict[str, str] = {}
    if DOTENV.exists():
        for line in DOTENV.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            values[key.strip()] = val.strip().strip('"').strip("'")
    values.update(os.environ)
    return values


def expand(value: str, env: dict[str, str]) -> tuple[str, list[str]]:
    """Expand $VAR / ${VAR} the way Meltano does. Returns (result, missing_names).

    Meltano substitutes an unset variable with an EMPTY STRING and says nothing,
    which silently yields a malformed URL -- so report the names instead.
    """
    missing: list[str] = []

    def sub(match: re.Match) -> str:
        name = match.group(1) or match.group(2)
        val = env.get(name, "")
        if not val:
            missing.append(name)
        return val

    return VAR_PATTERN.sub(sub, value), missing


def configured_tables() -> list[dict]:
    """Return every https table definition from meltano.yml."""
    try:
        import yaml
    except ImportError:
        sys.exit("PyYAML is required: pip install pyyaml")

    config = yaml.safe_load(MELTANO_YML.read_text())
    tables = []
    for extractor in config.get("plugins", {}).get("extractors", []):
        for table in (extractor.get("config") or {}).get("tables", []) or []:
            if str(table.get("path", "")).startswith("https://"):
                tables.append(table)
    return tables


def main() -> int:
    env = load_dotenv()
    tables = configured_tables()
    if not tables:
        print("No https table definitions found in meltano.yml", file=sys.stderr)
        return 2

    failed = 0
    for table in tables:
        name = table.get("name", "(unnamed)")
        path = table["path"]
        pattern = table.get("pattern", "")
        declared = len(table.get("field_names") or [])
        print(f"[{name}]")

        # meltano.yml sources the URL from .env, so expand it the way Meltano will.
        path, missing_path = expand(path, env)
        pattern, missing_pattern = expand(pattern, env)
        missing = missing_path + missing_pattern
        if missing:
            failed += 1
            for var in dict.fromkeys(missing):
                print(f"  FAIL  {var} is unset or empty in .env")
            print("        Meltano expands it to an empty string, producing a")
            print("        malformed URL with no error. Copy .env.example to .env")
            print("        and fill in every value.")
            continue

        # The tap requests exactly this: path + "/" + pattern.
        url = f"{path}/{pattern}"
        try:
            resp = urllib.request.urlopen(url, timeout=30)
            body = resp.read().decode("utf-8-sig", errors="replace")
        except urllib.error.HTTPError as exc:
            failed += 1
            print(f"  FAIL  HTTP {exc.code} {exc.reason}")
            print(f"        {url}")
            if exc.code in (401, 403):
                print("        The sheet is not readable without a login.")
                print("        Fix: Share > General access > 'Anyone with the link' (Viewer).")
            continue
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"  FAIL  {type(exc).__name__}: {exc}")
            continue

        ctype = resp.headers.get("Content-Type", "")
        if "text/csv" not in ctype:
            failed += 1
            print(f"  FAIL  expected text/csv, got {ctype!r}")
            print("        A login/consent page was returned instead of data.")
            continue

        rows = list(csv.reader(io.StringIO(body)))
        widths = {len(r) for r in rows}
        print(f"  OK    {len(rows)} rows, {len(body)} bytes, {max(widths, default=0)} columns")
        if rows:
            preview = ", ".join(c for c in rows[0][:6] if c)
            print(f"        first row: {preview or '(empty cells)'}")

        # The tap matches `pattern` as a regex against itself; metacharacters break it.
        if re.search(r"[?&=*+\[\](){}^$|]", pattern):
            failed += 1
            print(f"  FAIL  pattern {pattern!r} contains regex metacharacters.")
            print("        The tap would match 0 files and sync 0 rows silently.")

        # field_names must cover every column or trailing data is dropped.
        if declared and declared < max(widths, default=0):
            print(f"  WARN  {declared} field_names declared but sheet has "
                  f"{max(widths)} columns -- extra columns will be dropped.")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
