# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository.

## What this is

A healthcare MCP server built with FastMCP, serving 4 tools over Streamable
HTTP against a local SQLite database (`patients.db`) of synthetic patient
data. See `README.md` for the full tool table, setup, and architecture
diagram — this file focuses on conventions and gotchas for making changes.

## Setup / running

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python sqllite_onetime_db.py       # create patients.db + schema
python sqllite_onetime_tables.py   # seed sample data (safe to re-run)
python server.py                   # serves http://0.0.0.0:8000/mcp
```

There is no test suite or lint config. Verification is: run a tool module
directly (each has an `if __name__ == "__main__"` block), or run
`test_client.py` against a live server.

## Project layout and conventions

- `server.py` only registers tools — it must stay a thin wrapper layer.
  Business logic belongs in `tools/`, never in `server.py` itself.
- Each `@mcp.tool()` function in `server.py` is the contract an LLM client
  sees: its name, type hints, and docstring are used by FastMCP to generate
  the JSON schema. When changing a tool's signature or behavior, update the
  wrapper's docstring in `server.py` to match — stale docstrings will mislead
  calling agents, not just humans.
- Every module under `tools/` is independently runnable and imports
  `get_connection()` from `sqllite_onetime_db.py` directly — they do not
  depend on `server.py` or each other. Keep new tools in this same pattern:
  a plain function taking simple args, returning a dict, with its own
  `sys.path.insert(0, ...)` + `if __name__ == "__main__"` smoke test.
- `sqllite_onetime_db.py` (schema) and `sqllite_onetime_tables.py` (seed
  data) are one-time setup scripts, not part of the server's runtime import
  path. `patients.db` itself is gitignored — never assume it exists; it must
  be generated locally.
- `tools/query_patient_database`'s SQL safety check is a naive
  `.upper().startswith("SELECT")` string check — it is not a real SQL
  sandbox. Do not extend this tool's trust boundary (e.g. exposing it over a
  public network) without adding real query validation/sandboxing first.
- `server.py` sets `host="0.0.0.0"` and an explicit `transport_security`
  (`TransportSecuritySettings`) on the `FastMCP(...)` instance so the server
  can be reached from outside localhost. By default the MCP SDK auto-enables
  DNS-rebinding protection restricted to `127.0.0.1`/`localhost` Host headers
  whenever `host` isn't set — any other `Host` header gets a `421`, even
  though uvicorn itself binds to `0.0.0.0`. `ALLOWED_HOSTS` (env var, comma-
  separated, defaults to localhost-only) controls which Host headers are
  accepted; set it to the server's public IP/domain (with port) when exposing
  it remotely. Never put the actual IP/domain value into this repo — it's
  shell/env-only, same trust-boundary caution as the SQL tool above: host
  validation and CORS are not authentication.

## When adding a new tool

1. Write the logic in a new `tools/<name>.py` module (function takes simple
   args, returns a dict, uses `get_connection()`).
2. Add a corresponding `@mcp.tool()` wrapper in `server.py` with a precise
   docstring (Args/Returns) — this is what the calling LLM reads.
3. Add a standalone smoke test under `if __name__ == "__main__"` in the new
   module, following the pattern in the existing `tools/*.py` files.
4. Update the tool table in `README.md`.
