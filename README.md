# Healthcare MCP Server

A custom [MCP](https://modelcontextprotocol.io/) server exposing healthcare
analytics tools over Streamable HTTP, backed by a local SQLite database of
synthetic patient data. Built with FastMCP so each Python function becomes an
MCP tool automatically (schema generated from type hints + docstring).

- **Entry point:** `server.py` — registers the four tools below and serves
  them over Streamable HTTP at `http://0.0.0.0:8000/mcp`.
- **Data:** `patients.db` (gitignored, generated locally) — 10 synthetic
  patients with visits, diagnoses, medications, and lab results covering
  chronic conditions (diabetes, CHF, COPD, CKD, AFib, cancer in remission,
  etc.) plus one healthy baseline patient.
- **No external services:** everything runs locally — no API keys, no cloud
  dependencies.

## Tools

| Tool | File | What it does |
|---|---|---|
| `patient_risk_summary` | `tools/patient_risk_summary.py` | Scores a patient LOW/MEDIUM/HIGH based on chronic condition count, medication burden (polypharmacy), and abnormal lab results. |
| `readmission_insights` | `tools/re_admission_insight.py` | Assesses readmission risk (LOW/MODERATE/HIGH) from visit frequency (30/90/180-day windows), days since discharge, and recurring diagnoses. Returns a plain-English summary. |
| `database_schema` | `tools/schema_tool.py` | Introspects `patients.db` and returns table/column/type/row-count info. Meant to be called first so an agent can write valid SQL. |
| `query_database` | `tools/query_tool.py` | Runs an arbitrary **read-only** SQL query against `patients.db`. Rejects anything that isn't a `SELECT`. |

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Create and seed the database

The database is not checked into git. Build it once before starting the
server:

```bash
python sqllite_onetime_db.py       # creates patients.db and all 5 tables
python sqllite_onetime_tables.py   # seeds it with 10 sample patients
```

`sqllite_onetime_tables.py` is idempotent — it deletes existing rows before
re-inserting, so it's safe to re-run.

## Running a test query against the database

Once `patients.db` exists (after the seed step above), you can query it
directly with the `sqlite3` CLI, without going through the MCP server at all:

```bash
sqlite3 patients.db
```

Then at the `sqlite>` prompt:

```sql
.tables                              -- list all tables
.schema patients                     -- show a table's schema
SELECT * FROM patients LIMIT 5;      -- sample some rows
SELECT name, age FROM patients WHERE age > 70;
Insert into patients values (11,'Bob',90,'M','B+','555-1234','2026-10-12 13:24:54');
.quit
```

Or run a one-off query without entering the interactive shell:

```bash
sqlite3 patients.db "SELECT name, age, gender FROM patients ORDER BY age DESC;"
```

To exercise the same read-only path the MCP server uses (including the
`SELECT`-only safety check), call the `query_tool.py` module directly instead:

```bash
python tools/query_tool.py
```

This runs a few canned queries (a valid `SELECT`, a rejected `DELETE`, and a
`JOIN`) and prints the JSON each one returns.

## Running the server

```bash
python server.py
```

Starts a Streamable HTTP MCP server at `http://0.0.0.0:8000/mcp` with CORS
enabled (so browser-based tools like MCP Inspector can connect).

### Accessing it from another machine (e.g. a VPS)

The MCP SDK rejects any request whose `Host` header isn't `127.0.0.1`/
`localhost` by default (DNS-rebinding protection), even though uvicorn binds
to `0.0.0.0`. To reach the server from outside the host, set `ALLOWED_HOSTS`
to the host/IP clients will connect through (comma-separated, `:*` matches
any port).

This is optional and read from a local `.env` file (via `python-dotenv`),
so the same `server.py` runs unchanged on your laptop and on a VPS — no
`.env` present just means it falls back to the localhost-only default:

```bash
cp .env.example .env
# edit .env and set ALLOWED_HOSTS to the real public IP/domain:port
python server.py
```

`.env` is gitignored — never commit the real IP/domain. You can still use
`export ALLOWED_HOSTS=...` instead of `.env` if you prefer; the env var
takes the same effect either way.

You'll also need the firewall to allow inbound traffic on port 8000 (e.g.
`sudo ufw allow 8000/tcp`). Treat this the same as the SQL-query trust-boundary
note above: don't expose this server to untrusted networks without adding
real auth in front of it (API key, reverse proxy with TLS, etc.) — CORS and
host checks alone don't authenticate callers.

## Testing

Each tool module can be run standalone to exercise its logic directly against
the database, without going through MCP at all:

```bash
python tools/patient_risk_summary.py
python tools/re_admission_insight.py
python tools/schema_tool.py
python tools/query_tool.py
```

To test the full MCP wire protocol, start the server in one terminal and run
the manual client in another:

```bash
# terminal 1
python server.py

# terminal 2
python test_client.py
```

`test_client.py` connects over Streamable HTTP, lists the registered tools,
and calls `database_schema` to confirm the round trip works.

## Architecture notes

```
 MCP client            server.py                tools/*.py              patients.db
 (test_client.py,  ──▶  FastMCP           ──▶   plain Python       ──▶  SQLite
  Claude Desktop,        @mcp.tool()             functions,              (patients,
  MCP Inspector...)      wrappers                each opens its          visits,
                                                  own sqlite3             diagnoses,
                                                  connection              medications,
                                                                          lab_results)
```

- `server.py` is a thin registration layer: each `@mcp.tool()` function is a
  one-line wrapper that calls into `tools/`. Docstrings and type hints on the
  wrapper functions are what FastMCP uses to generate the JSON schema clients
  see — keep them accurate when adding tools.
- Each module under `tools/` is self-contained and opens its own DB
  connection via `sqllite_onetime_db.get_connection()`; none of them import
  from `server.py`, so they can be run and tested independently (see the
  `if __name__ == "__main__"` block in each file).
- `query_patient_database` (`tools/query_tool.py`) is the only tool that
  executes free-form SQL. Its only safety guard is a string check that the
  query starts with `SELECT` — it is not a full SQL sandbox (no protection
  against multi-statement injection, `PRAGMA`, etc.), so treat it as
  trusted-input-only / local-dev-only, not something to expose to untrusted
  callers.
- The five tables (`patients`, `visits`, `diagnoses`, `medications`,
  `lab_results`) are linked by `patient_id`; `visits` is also referenced by
  `diagnoses` and `lab_results` via `visit_id`. Run `database_schema` (or
  read `sqllite_onetime_db.py`) to see exact columns before writing queries.
