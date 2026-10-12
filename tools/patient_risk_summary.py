"""
Tool 1A: get_patient_risk_summary
----------------------------------
Computes a risk profile for a patient by querying across all tables.

Risk Tier logic:
  LOW    — 0 to 2 abnormal signals
  MEDIUM — 3 to 4 abnormal signals
  HIGH   — 5 or more abnormal signals

Run independently to test:
    python tools/risk_summary.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # add project root to path

from sqllite_onetime_db import get_connection


def get_patient_risk_summary(patient_id: int) -> dict:
    """
    Accepts a patient_id and returns a structured risk profile.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # --- 1. Fetch basic patient demographics ---
    cursor.execute("""
        SELECT patient_id, name, age, gender, blood_type
        FROM patients
        WHERE patient_id = ?
    """, (patient_id,))
    patient = cursor.fetchone()

    if not patient:
        conn.close()
        return {"error": f"Patient with ID {patient_id} not found."}

    # --- 2. Count active chronic diagnoses ---
    cursor.execute("""
        SELECT COUNT(DISTINCT diagnosis_name) AS chronic_count
        FROM diagnoses
        WHERE patient_id = ?
          AND diagnosis_type = 'chronic'
    """, (patient_id,))
    chronic_count = cursor.fetchone()["chronic_count"]

    # --- 3. Count active medications (medication burden) ---
    cursor.execute("""
        SELECT COUNT(*) AS med_count
        FROM medications
        WHERE patient_id = ?
          AND is_active = 1
    """, (patient_id,))
    active_med_count = cursor.fetchone()["med_count"]

    # --- 4. Fetch latest lab results and flag abnormal ones ---
    # We get the most recent result for each test type
    cursor.execute("""
        SELECT test_name, result_value, unit, reference_range, is_abnormal, test_date
        FROM lab_results
        WHERE patient_id = ?
        ORDER BY test_date DESC
    """, (patient_id,))
    all_labs = [dict(row) for row in cursor.fetchall()]

    # Keep only the latest result per test (test_name is unique after ordering by date)
    seen_tests = set()
    latest_labs = []
    for lab in all_labs:
        if lab["test_name"] not in seen_tests:
            seen_tests.add(lab["test_name"])
            latest_labs.append(lab)

    # Count how many of the latest labs are flagged abnormal
    abnormal_labs = [lab for lab in latest_labs if lab["is_abnormal"] == 1]
    abnormal_count = len(abnormal_labs)

    conn.close()

    # --- 5. Compute total risk signals and assign tier ---
    # Each of these counts as a risk signal:
    #   - Each chronic condition (capped at 3 for scoring)
    #   - Each 2 active medications beyond 2 count as 1 signal (polypharmacy)
    #   - Each abnormal lab result
    chronic_signal   = min(chronic_count, 3)           # cap at 3
    polypharmacy_signal = max(0, (active_med_count - 2) // 2)  # every 2 extra meds = 1 signal
    total_signals    = chronic_signal + polypharmacy_signal + abnormal_count

    if total_signals <= 2:
        risk_tier = "LOW"
    elif total_signals <= 4:
        risk_tier = "MEDIUM"
    else:
        risk_tier = "HIGH"

    # --- 6. Return structured result ---
    return {
        "patient": {
            "patient_id":  patient["patient_id"],
            "name":        patient["name"],
            "age":         patient["age"],
            "gender":      patient["gender"],
            "blood_type":  patient["blood_type"],
        },
        "risk_factors": {
            "chronic_condition_count": chronic_count,
            "active_medication_count": active_med_count,
            "abnormal_lab_count":      abnormal_count,
            "abnormal_labs":           abnormal_labs,
        },
        "scoring": {
            "chronic_signal":      chronic_signal,
            "polypharmacy_signal": polypharmacy_signal,
            "total_signals":       total_signals,
        },
        "risk_tier": risk_tier,
    }


# ---------- Quick test ----------
if __name__ == "__main__":
    import json
    for pid in [1, 4, 8]:  # Margaret (HIGH), James (HIGH), Charles (LOW)
        result = get_patient_risk_summary(pid)
        print(f"\n=== Patient {pid} ===")
        print(json.dumps(result, indent=2))

