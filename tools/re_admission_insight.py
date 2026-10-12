"""
Tool 1B: get_readmission_insights
-----------------------------------
Analyzes a patient's visit history to assess readmission risk.

Readmission Risk logic:
  LOW      — 0-1 visits in 90 days AND no recurring diagnoses
  MODERATE — 2 visits in 90 days OR recurring diagnoses
  HIGH     — 3+ visits in 90 days, OR recent discharge (<30 days) with recurring diagnoses

Run independently to test:
    python tools/readmission.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqllite_onetime_db import get_connection
from datetime import date, datetime, timedelta


def _parse_date(date_str: str) -> date:
    """Helper to parse 'YYYY-MM-DD' strings into date objects."""
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def get_readmission_insights(patient_id: int) -> dict:
    """
    Accepts a patient_id and returns a readmission risk assessment.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Verify patient exists
    cursor.execute("SELECT name FROM patients WHERE patient_id = ?", (patient_id,))
    patient = cursor.fetchone()
    if not patient:
        conn.close()
        return {"error": f"Patient with ID {patient_id} not found."}

    patient_name = patient["name"]
    today = date.today()

    # --- 1. Fetch all visits ordered by most recent first ---
    cursor.execute("""
        SELECT visit_id, visit_date, discharge_date, visit_type, department
        FROM visits
        WHERE patient_id = ?
        ORDER BY visit_date DESC
    """, (patient_id,))
    visits = [dict(row) for row in cursor.fetchall()]

    # --- 2. Count visits in last 30, 90, and 180 days ---
    def count_visits_in_days(days: int) -> int:
        cutoff = today - timedelta(days=days)
        return sum(1 for v in visits if _parse_date(v["visit_date"]) >= cutoff)

    visits_last_30  = count_visits_in_days(30)
    visits_last_90  = count_visits_in_days(90)
    visits_last_180 = count_visits_in_days(180)

    # --- 3. Calculate days since last discharge ---
    days_since_discharge = None
    last_discharge_date  = None

    if visits and visits[0]["discharge_date"]:
        last_discharge_date = _parse_date(visits[0]["discharge_date"])
        days_since_discharge = (today - last_discharge_date).days

    # --- 4. Detect recurring diagnoses ---
    # A diagnosis is "recurring" if the same diagnosis_name appears in 2+ different visits
    cursor.execute("""
        SELECT diagnosis_name, COUNT(DISTINCT visit_id) AS visit_count
        FROM diagnoses
        WHERE patient_id = ?
        GROUP BY diagnosis_name
        HAVING visit_count >= 2
    """, (patient_id,))
    recurring = [dict(row) for row in cursor.fetchall()]
    has_recurring = len(recurring) > 0

    conn.close()

    # --- 5. Compute readmission risk level ---
    if visits_last_90 >= 3 or (days_since_discharge is not None and days_since_discharge < 30 and has_recurring):
        risk_level = "HIGH"
    elif visits_last_90 >= 2 or has_recurring:
        risk_level = "MODERATE"
    else:
        risk_level = "LOW"

    # --- 6. Generate a plain-English summary ---
    if risk_level == "HIGH":
        summary = (
            f"{patient_name} has {visits_last_90} visits in the past 90 days"
            + (f" and was discharged {days_since_discharge} days ago" if days_since_discharge is not None else "")
            + (f", with {len(recurring)} recurring condition(s)" if has_recurring else "")
            + " — high readmission risk."
        )
    elif risk_level == "MODERATE":
        summary = (
            f"{patient_name} has {visits_last_90} visit(s) in the past 90 days"
            + (f" with recurring diagnoses ({', '.join(r['diagnosis_name'] for r in recurring[:2])})" if has_recurring else "")
            + " — moderate readmission risk."
        )
    else:
        summary = (
            f"{patient_name} has had {visits_last_180} visit(s) in the past 180 days"
            + " with no significant readmission risk indicators."
        )

    # --- 7. Return structured result ---
    return {
        "patient_id":    patient_id,
        "patient_name":  patient_name,
        "visit_counts": {
            "last_30_days":  visits_last_30,
            "last_90_days":  visits_last_90,
            "last_180_days": visits_last_180,
        },
        "days_since_last_discharge":  days_since_discharge,
        "last_discharge_date":        str(last_discharge_date) if last_discharge_date else None,
        "has_recurring_diagnoses":    has_recurring,
        "recurring_diagnoses":        recurring,
        "readmission_risk":           risk_level,
        "summary":                    summary,
    }


# ---------- Quick test ----------
if __name__ == "__main__":
    import json
    for pid in [4, 1, 8]:  # James (HIGH), Margaret (HIGH), Charles (LOW)
        result = get_readmission_insights(pid)
        print(f"\n=== Patient {pid} ===")
        print(json.dumps(result, indent=2))

