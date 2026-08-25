#!/usr/bin/env python3
"""Mint a Google OAuth refresh token for tap-google-sheets.

Prerequisite (one-off, in the Google Cloud console):
  1. Create/pick a project:      https://console.cloud.google.com/projectcreate
  2. Enable the Sheets API:      https://console.cloud.google.com/apis/library/sheets.googleapis.com
  3. Configure the OAuth consent screen (External is fine; add yourself as a Test user).
  4. Credentials > Create credentials > OAuth client ID > Application type "Desktop app".
     Copy the Client ID and Client secret.

Then run:
    python3 extract/google_oauth_setup.py

It opens a browser, catches the redirect on localhost, exchanges the code, and prints
the three .env lines to paste into .env. Uses only the standard library.

The token is printed to your terminal only -- nothing is uploaded anywhere except
Google's own token endpoint.
"""
from __future__ import annotations

import http.server
import json
import secrets
import socketserver
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

SCOPE = "https://www.googleapis.com/auth/spreadsheets.readonly"
AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
PORT = 8723
REDIRECT_URI = f"http://localhost:{PORT}/"

_result: dict[str, str] = {}
_done = threading.Event()


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        _result.update({k: v[0] for k, v in params.items()})

        ok = "code" in _result
        body = (
            b"<h2>Authorised.</h2><p>Return to your terminal.</p>"
            if ok
            else b"<h2>Authorisation failed.</h2><p>Check the terminal for details.</p>"
        )
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        _done.set()

    def log_message(self, *_args):
        pass


def post_form(url: str, data: dict[str, str]) -> dict:
    encoded = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(
        url, data=encoded, headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise SystemExit(f"Token exchange failed: HTTP {exc.code}\n{detail}") from exc


def main() -> int:
    print(__doc__.split("Then run:")[0].rstrip())
    print("-" * 70)
    try:
        client_id = input("Client ID: ").strip()
        client_secret = input("Client secret: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nAborted -- this script needs an interactive terminal.", file=sys.stderr)
        return 130
    if not client_id or not client_secret:
        print("Both values are required.", file=sys.stderr)
        return 2

    print()
    print("In the Google console, make sure this OAuth client lists the redirect URI:")
    print(f"    {REDIRECT_URI}")
    print("(Desktop app clients usually accept any localhost port automatically.)")
    print()

    state = secrets.token_urlsafe(16)
    auth_url = f"{AUTH_ENDPOINT}?" + urllib.parse.urlencode(
        {
            "client_id": client_id,
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "scope": SCOPE,
            "access_type": "offline",
            "prompt": "consent",  # force a refresh_token even on re-auth
            "state": state,
        }
    )

    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer(("127.0.0.1", PORT), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    print("Opening your browser to authorise...")
    print(f"If it does not open, visit:\n  {auth_url}\n")
    try:
        webbrowser.open(auth_url)
    except Exception:  # noqa: BLE001
        pass

    if not _done.wait(timeout=300):
        server.shutdown()
        print("Timed out waiting for the browser redirect.", file=sys.stderr)
        return 1
    server.shutdown()

    if "error" in _result:
        print(f"Authorisation denied: {_result['error']}", file=sys.stderr)
        return 1
    if _result.get("state") != state:
        print("State mismatch -- aborting.", file=sys.stderr)
        return 1

    tokens = post_form(
        TOKEN_ENDPOINT,
        {
            "code": _result["code"],
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
        },
    )

    refresh_token = tokens.get("refresh_token")
    if not refresh_token:
        print(
            "Google did not return a refresh_token. Revoke prior access at "
            "https://myaccount.google.com/permissions and try again.",
            file=sys.stderr,
        )
        return 1

    print("\n" + "=" * 70)
    print("Success. Append these lines to .env (which is gitignored):\n")
    print(f"TAP_GOOGLE_SHEETS_OAUTH_CREDENTIALS_CLIENT_ID={client_id}")
    print(f"TAP_GOOGLE_SHEETS_OAUTH_CREDENTIALS_CLIENT_SECRET={client_secret}")
    print(f"TAP_GOOGLE_SHEETS_OAUTH_CREDENTIALS_REFRESH_TOKEN={refresh_token}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
