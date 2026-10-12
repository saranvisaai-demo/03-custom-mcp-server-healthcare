"""
Tool 2B: query_patient_database
----------------------------------
Accepts a SQL SELECT query and executes it against patients.db.

Safety guardrail: Only SELECT statements are allowed.
Any INSERT, UPDATE, DELETE, DROP, etc. will be rejected.

Run independently to test:
    python tools/query_tool.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqllite_onetime_db import get_connection


def query_patient_database(sql_query: str, max_rows: int = 10) -> dict:
    """
    Executes a read-only SQL query and returns the results.

    Args:
        sql_query: A SQL SELECT statement to run.
        max_rows:  Maximum number of rows to return (default 50).

    Returns:
        A dict with: results, sql, row_count, status, and error (if any).
    """
    print(sql_query)
    # --- Safety check: only allow SELECT statements ---
    # Strip leading whitespace and check the first keyword
    cleaned = sql_query.strip().upper()
    if not cleaned.startswith("SELECT"):
        return {
            "status":    "error",
            "error":     "Only SELECT statements are allowed. Write operations are not permitted.",
            "sql":       sql_query,
            "results":   [],
            "row_count": 0,
        }

    # --- Execute the query ---
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Apply row limit directly in Python (LIMIT may already be in the query)
        cursor.execute(sql_query)
        rows = cursor.fetchmany(max_rows)  # fetch up to max_rows

        # Convert sqlite3.Row objects to plain dicts
        results = [dict(row) for row in rows]
        row_count = len(results)

        conn.close()

        return {
            "status":    "success",
            "sql":       sql_query,
            "row_count": row_count,
            "results":   results,
        }

    except Exception as e:
        return {
            "status":    "error",
            "error":     str(e),
            "sql":       sql_query,
            "results":   [],
            "row_count": 0,
        }


# ---------- Quick test (This section is only for testing the tool separately)----------
if __name__ == "__main__":
    import json

    # Test 1: valid SELECT
    q1 = "SELECT name, age, gender FROM patients ORDER BY age DESC"
    print("=== Test 1: Valid SELECT ===")
    print(json.dumps(query_patient_database(q1), indent=2))

    # Test 2: rejected write operation
    q2 = "DELETE FROM patients WHERE patient_id = 1"
    print("\n=== Test 2: Rejected DELETE ===")
    print(json.dumps(query_patient_database(q2), indent=2))

    # Test 3: join query
    q3 = """
        SELECT p.name, d.diagnosis_name, d.diagnosis_type
        FROM patients p
        JOIN diagnoses d ON p.patient_id = d.patient_id
        WHERE d.diagnosis_type = 'chronic'
        LIMIT 10
    """
    print("\n=== Test 3: JOIN query ===")
    print(json.dumps(query_patient_database(q3), indent=2))

