"""
Tool 2A: get_database_schema
------------------------------
Introspects the SQLite database and returns a clean representation
of all tables, their columns, and data types.

This is a utility tool — it helps an AI agent understand the schema
before it constructs SQL queries via the query_patient_database tool.

Run independently to test:
    python tools/schema_tool.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqllite_onetime_db import get_connection


def get_database_schema() -> dict:
    """
    Returns a dictionary describing all tables and their columns.
    No parameters needed — it describes the entire database.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Get list of all user-created tables (exclude SQLite internal tables)
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    tables = [row["name"] for row in cursor.fetchall()]

    schema = {}

    for table_name in tables:
        # PRAGMA table_info returns one row per column with:
        # cid, name, type, notnull, dflt_value, pk
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = cursor.fetchall()

        columns = []
        for col in columns_info:
            columns.append({
                "column":      col["name"],
                "type":        col["type"],
                "not_null":    bool(col["notnull"]),
                "primary_key": bool(col["pk"]),
                "default":     col["dflt_value"],
            })

        # Get row count so the agent knows how much data is available
        cursor.execute(f"SELECT COUNT(*) AS cnt FROM {table_name}")
        row_count = cursor.fetchone()["cnt"]

        schema[table_name] = {
            "columns":   columns,
            "row_count": row_count,
        }

    conn.close()

    return {
        "database": "patients.db",
        "tables":   schema,
        "table_count": len(tables),
    }


# ---------- Quick test ----------
if __name__ == "__main__":
    import json
    result = get_database_schema()
    print(json.dumps(result, indent=2))

