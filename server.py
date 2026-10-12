"""
server.py — Healthcare MCP Server
------------------------------------
Registers all four healthcare tools with the MCP SDK and
runs the server using Streamable HTTP transport (the latest MCP standard).

Start the server:
    python server.py

The server listens on:
    http://0.0.0.0:8000/mcp
"""

from mcp.server.fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware

# Import the four tool functions we built
from tools.patient_risk_summary  import get_patient_risk_summary
from tools.re_admission_insight   import get_readmission_insights
from tools.schema_tool   import get_database_schema
from tools.query_tool    import query_patient_database

# --------------------------------------------------------------------------
# Create the MCP server instance
# FastMCP handles tool registration, schema generation, and SSE transport
# --------------------------------------------------------------------------
mcp = FastMCP(
    name="healthcare-mcp-server"
)
# --------------------------------------------------------------------------
# Tool 1A — Patient Risk Summary
# The @mcp.tool() decorator registers the function as an MCP tool.
# FastMCP reads the type hints and docstring to auto-generate the JSON schema.
# --------------------------------------------------------------------------
@mcp.tool()
def patient_risk_summary(patient_id: int) -> dict:
    """
    Compute a risk profile for a patient.

    Queries patient demographics, chronic diagnoses, active medications,
    and latest lab results to produce a risk tier: LOW, MEDIUM, or HIGH.

    Args:
        patient_id: The unique integer ID of the patient.

    Returns:
        A dict with patient info, risk factors, scoring signals, and risk tier.
    """
    return get_patient_risk_summary(patient_id)


# --------------------------------------------------------------------------
# Tool 1B — Readmission Insights
# --------------------------------------------------------------------------
@mcp.tool()
def readmission_insights(patient_id: int) -> dict:
    """
    Analyze a patient's visit history to assess readmission risk.

    Counts recent visits (last 30/90/180 days), calculates days since
    last discharge, detects recurring diagnoses, and returns a risk
    level (LOW, MODERATE, HIGH) with a plain-English summary.

    Args:
        patient_id: The unique integer ID of the patient.

    Returns:
        A dict with visit counts, discharge info, recurring diagnoses,
        readmission risk level, and a one-line summary.
    """
    return get_readmission_insights(patient_id)


# --------------------------------------------------------------------------
# Tool 2A — Database Schema
# --------------------------------------------------------------------------
@mcp.tool()
def database_schema() -> dict:
    """
    Retrieve the schema of the patients.db SQLite database.

    Returns all table names, their column names and types, and row counts.
    Use this tool first to understand the database structure before
    writing SQL queries with the query_patient_database tool.

    Returns:
        A dict describing all tables, columns, types, and row counts.
    """
    return get_database_schema()


# --------------------------------------------------------------------------
# Tool 2B — Query Patient Database
# --------------------------------------------------------------------------
@mcp.tool()
def query_database(sql_query: str, max_rows: int = 50) -> dict:
    """
    Execute a read-only SQL SELECT query against patients.db.

    Only SELECT statements are allowed — any attempt to run INSERT,
    UPDATE, DELETE, DROP, or other write operations will be rejected
    with an error message.

    Args:
        sql_query: A valid SQL SELECT statement.
        max_rows:  Maximum number of rows to return (default 50).

    Returns:
        A dict with: results (list of dicts), sql, row_count, and status.
    """
    return query_patient_database(sql_query, max_rows)


app = mcp.streamable_http_app()  # Streamable HTTP transport (replaces SSE)


# --------------------------------------------------------------------------
# Add CORS middleware so browser-based tools (MCP Inspector, etc.) can connect
# --------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Allow all origins
    allow_methods=["*"],       # Allow all HTTP methods
    allow_headers=["*"],       # Allow all headers
)

# --------------------------------------------------------------------------
# Run the server with Streamable HTTP transport
# --------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    print("Starting Healthcare MCP Server on http://0.0.0.0:8000/mcp")
    uvicorn.run(app, host="0.0.0.0", port=8000)

