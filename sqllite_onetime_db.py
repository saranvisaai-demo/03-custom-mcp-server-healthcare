import sqlite3
import os

# Path to the SQLite database file
DB_PATH = os.path.join(os.path.dirname(__file__), "patients.db")


def get_connection():
    """
    Returns a SQLite connection with row_factory set to sqlite3.Row
    so that query results can be accessed like dictionaries.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    return conn


def create_tables():
    """
    Creates all four tables in the database if they don't already exist.
    Run this once before seeding data.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # --- Patients table: core demographic info ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT NOT NULL,
            age             INTEGER,
            gender          TEXT,
            blood_type      TEXT,
            contact_number  TEXT,
            created_at      TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --- Visits table: each hospital visit ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visits (
            visit_id          INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id        INTEGER,
            visit_date        TEXT,
            discharge_date    TEXT,
            visit_type        TEXT,   -- e.g. Emergency, Routine, Follow-up
            department        TEXT,
            attending_doctor  TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
        )
    """)

    # --- Diagnoses table: medical diagnoses per visit ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diagnoses (
            diagnosis_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id      INTEGER,
            visit_id        INTEGER,
            diagnosis_code  TEXT,    -- ICD-10 style code
            diagnosis_name  TEXT,
            diagnosis_type  TEXT,    -- 'acute' or 'chronic'
            diagnosed_date  TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
            FOREIGN KEY (visit_id)   REFERENCES visits(visit_id)
        )
    """)

    # --- Medications table: current and past prescriptions ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medications (
            medication_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id      INTEGER,
            medication_name TEXT,
            dosage          TEXT,
            start_date      TEXT,
            end_date        TEXT,
            is_active       INTEGER DEFAULT 1,  -- 1 = active, 0 = stopped
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
        )
    """)

    # --- Lab Results table: test results per visit ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lab_results (
            lab_id           INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id       INTEGER,
            visit_id         INTEGER,
            test_name        TEXT,
            result_value     REAL,
            unit             TEXT,
            reference_range  TEXT,
            is_abnormal      INTEGER DEFAULT 0,  -- 1 = abnormal, 0 = normal
            test_date        TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
            FOREIGN KEY (visit_id)   REFERENCES visits(visit_id)
        )
    """)

    conn.commit()
    conn.close()
    print("All tables created successfully.")


# Allow running this file directly to initialize the DB
if __name__ == "__main__":
    create_tables()

