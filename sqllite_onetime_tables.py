"""
sqllite_onetime_tables.py — Populates patients.db with realistic sample data.

Run this script once after creating the database:
    python sqllite_onetime_tables.py

Includes 10 patients with varied conditions:
  - Diabetic patients
  - Cardiac patients
  - Elderly patients with multiple chronic conditions
  - A healthy young patient (low risk baseline)
"""

from sqllite_onetime_db import get_connection, create_tables

# --------------------------------------------------------------------------
# Patient demographics
# --------------------------------------------------------------------------
PATIENTS = [
    # (name, age, gender, blood_type, contact_number)
    ("Margaret Collins",  72, "F", "A+",  "555-0101"),   # P1 — elderly, diabetic + cardiac
    ("Robert Nguyen",     65, "M", "O+",  "555-0102"),   # P2 — cardiac, hypertension
    ("Linda Patel",       58, "F", "B+",  "555-0103"),   # P3 — diabetic, CKD
    ("James Walker",      81, "M", "AB+", "555-0104"),   # P4 — elderly, COPD, heart failure
    ("Susan Martinez",    47, "F", "A-",  "555-0105"),   # P5 — asthma, anxiety
    ("David Kim",         55, "M", "O-",  "555-0106"),   # P6 — Type 2 diabetes, obesity
    ("Barbara Thompson",  69, "F", "B-",  "555-0107"),   # P7 — atrial fibrillation, stroke hx
    ("Charles Brown",     38, "M", "A+",  "555-0108"),   # P8 — healthy, one acute visit
    ("Patricia Davis",    74, "F", "O+",  "555-0109"),   # P9 — osteoporosis, depression, HTN
    ("Michael Johnson",   62, "M", "AB-", "555-0110"),   # P10 — cancer in remission, diabetes
]

# --------------------------------------------------------------------------
# Hospital visits — (patient_index 0-based, visit_date, discharge_date,
#                    visit_type, department, attending_doctor)
# --------------------------------------------------------------------------
VISITS = [
    # Margaret Collins (P1) — frequent visits
    (0, "2024-01-10", "2024-01-14", "Emergency",  "Cardiology",    "Dr. Reeves"),
    (0, "2024-03-22", "2024-03-25", "Follow-up",  "Endocrinology", "Dr. Shah"),
    (0, "2024-06-05", "2024-06-08", "Emergency",  "Cardiology",    "Dr. Reeves"),
    (0, "2024-09-18", "2024-09-20", "Routine",    "Endocrinology", "Dr. Shah"),
    (0, "2024-12-01", "2024-12-04", "Emergency",  "Cardiology",    "Dr. Reeves"),

    # Robert Nguyen (P2) — cardiac follow-ups
    (1, "2024-02-14", "2024-02-17", "Emergency",  "Cardiology",    "Dr. Reeves"),
    (1, "2024-05-30", "2024-06-01", "Follow-up",  "Cardiology",    "Dr. Reeves"),
    (1, "2024-11-10", "2024-11-12", "Routine",    "Cardiology",    "Dr. Reeves"),

    # Linda Patel (P3) — diabetes + kidney
    (2, "2024-03-05", "2024-03-07", "Emergency",  "Nephrology",    "Dr. Okafor"),
    (2, "2024-07-22", "2024-07-24", "Routine",    "Endocrinology", "Dr. Shah"),
    (2, "2024-10-15", "2024-10-16", "Follow-up",  "Nephrology",    "Dr. Okafor"),

    # James Walker (P4) — very high risk elderly
    (3, "2024-01-08", "2024-01-15", "Emergency",  "Pulmonology",   "Dr. Cho"),
    (3, "2024-02-20", "2024-02-25", "Emergency",  "Cardiology",    "Dr. Reeves"),
    (3, "2024-04-10", "2024-04-14", "Follow-up",  "Pulmonology",   "Dr. Cho"),
    (3, "2024-06-28", "2024-07-02", "Emergency",  "Cardiology",    "Dr. Reeves"),
    (3, "2024-09-05", "2024-09-09", "Emergency",  "Pulmonology",   "Dr. Cho"),
    (3, "2024-11-30", "2024-12-05", "Emergency",  "Cardiology",    "Dr. Reeves"),

    # Susan Martinez (P5) — moderate, asthma
    (4, "2024-04-18", "2024-04-19", "Emergency",  "Pulmonology",   "Dr. Cho"),
    (4, "2024-09-10", "2024-09-10", "Routine",    "Primary Care",  "Dr. Pham"),

    # David Kim (P6) — diabetes, obesity
    (5, "2024-03-12", "2024-03-14", "Routine",    "Endocrinology", "Dr. Shah"),
    (5, "2024-08-05", "2024-08-07", "Emergency",  "Endocrinology", "Dr. Shah"),
    (5, "2024-11-20", "2024-11-21", "Follow-up",  "Endocrinology", "Dr. Shah"),

    # Barbara Thompson (P7) — AFib, stroke history
    (6, "2024-02-01", "2024-02-07", "Emergency",  "Neurology",     "Dr. Chen"),
    (6, "2024-05-14", "2024-05-16", "Follow-up",  "Cardiology",    "Dr. Reeves"),
    (6, "2024-10-22", "2024-10-24", "Emergency",  "Cardiology",    "Dr. Reeves"),

    # Charles Brown (P8) — healthy, one acute episode
    (7, "2024-07-04", "2024-07-05", "Emergency",  "General Surgery","Dr. Adams"),

    # Patricia Davis (P9) — multiple chronic issues
    (8, "2024-02-28", "2024-03-02", "Emergency",  "Orthopedics",   "Dr. Lee"),
    (8, "2024-06-15", "2024-06-16", "Routine",    "Primary Care",  "Dr. Pham"),
    (8, "2024-10-08", "2024-10-10", "Follow-up",  "Psychiatry",    "Dr. Torres"),

    # Michael Johnson (P10) — cancer remission + diabetes
    (9, "2024-03-20", "2024-03-24", "Emergency",  "Oncology",      "Dr. Rivera"),
    (9, "2024-07-08", "2024-07-09", "Routine",    "Oncology",      "Dr. Rivera"),
    (9, "2024-11-05", "2024-11-07", "Follow-up",  "Endocrinology", "Dr. Shah"),
]

# --------------------------------------------------------------------------
# Diagnoses — (patient_index, visit_index, code, name, type, date)
# --------------------------------------------------------------------------
DIAGNOSES = [
    # Margaret Collins — diabetes + CHF + hypertension
    (0, 0,  "I50.9",  "Congestive Heart Failure",          "chronic", "2024-01-10"),
    (0, 0,  "E11.9",  "Type 2 Diabetes Mellitus",          "chronic", "2024-01-10"),
    (0, 1,  "E11.9",  "Type 2 Diabetes Mellitus",          "chronic", "2024-03-22"),
    (0, 2,  "I50.9",  "Congestive Heart Failure",          "chronic", "2024-06-05"),
    (0, 2,  "I10",    "Essential Hypertension",            "chronic", "2024-06-05"),
    (0, 4,  "I50.9",  "Congestive Heart Failure",          "chronic", "2024-12-01"),

    # Robert Nguyen — CAD + hypertension
    (1, 5,  "I25.10", "Coronary Artery Disease",           "chronic", "2024-02-14"),
    (1, 5,  "I10",    "Essential Hypertension",            "chronic", "2024-02-14"),
    (1, 6,  "I25.10", "Coronary Artery Disease",           "chronic", "2024-05-30"),
    (1, 7,  "I25.10", "Coronary Artery Disease",           "chronic", "2024-11-10"),
    (1, 7,  "I10",    "Essential Hypertension",            "chronic", "2024-11-10"),

    # Linda Patel — diabetes + CKD
    (2, 8,  "E11.9",  "Type 2 Diabetes Mellitus",          "chronic", "2024-03-05"),
    (2, 8,  "N18.3",  "Chronic Kidney Disease Stage 3",    "chronic", "2024-03-05"),
    (2, 9,  "E11.9",  "Type 2 Diabetes Mellitus",          "chronic", "2024-07-22"),
    (2, 10, "N18.3",  "Chronic Kidney Disease Stage 3",    "chronic", "2024-10-15"),

    # James Walker — COPD + heart failure + pneumonia (recurring acute)
    (3, 11, "J44.1",  "COPD Exacerbation",                 "chronic", "2024-01-08"),
    (3, 11, "I50.9",  "Congestive Heart Failure",          "chronic", "2024-01-08"),
    (3, 12, "I50.9",  "Congestive Heart Failure",          "chronic", "2024-02-20"),
    (3, 12, "J18.9",  "Pneumonia",                         "acute",   "2024-02-20"),
    (3, 13, "J44.1",  "COPD Exacerbation",                 "chronic", "2024-04-10"),
    (3, 14, "I50.9",  "Congestive Heart Failure",          "chronic", "2024-06-28"),
    (3, 15, "J44.1",  "COPD Exacerbation",                 "chronic", "2024-09-05"),
    (3, 16, "I50.9",  "Congestive Heart Failure",          "chronic", "2024-11-30"),
    (3, 16, "J18.9",  "Pneumonia",                         "acute",   "2024-11-30"),

    # Susan Martinez — asthma + anxiety
    (4, 17, "J45.41", "Moderate Persistent Asthma",        "chronic", "2024-04-18"),
    (4, 18, "F41.1",  "Generalized Anxiety Disorder",      "chronic", "2024-09-10"),

    # David Kim — T2DM + obesity + hyperlipidemia
    (5, 19, "E11.9",  "Type 2 Diabetes Mellitus",          "chronic", "2024-03-12"),
    (5, 19, "E66.9",  "Obesity",                           "chronic", "2024-03-12"),
    (5, 20, "E11.65", "T2DM with Hyperglycemia",           "acute",   "2024-08-05"),
    (5, 21, "E78.5",  "Hyperlipidemia",                    "chronic", "2024-11-20"),

    # Barbara Thompson — AFib + stroke history + HTN
    (6, 22, "I63.9",  "Cerebral Infarction (Stroke)",      "acute",   "2024-02-01"),
    (6, 22, "I48.91", "Atrial Fibrillation",               "chronic", "2024-02-01"),
    (6, 23, "I48.91", "Atrial Fibrillation",               "chronic", "2024-05-14"),
    (6, 24, "I48.91", "Atrial Fibrillation",               "chronic", "2024-10-22"),
    (6, 24, "I10",    "Essential Hypertension",            "chronic", "2024-10-22"),

    # Charles Brown — appendicitis (acute, resolved)
    (7, 25, "K35.80", "Acute Appendicitis",                "acute",   "2024-07-04"),

    # Patricia Davis — osteoporosis + depression + HTN
    (8, 26, "M81.0",  "Osteoporosis",                      "chronic", "2024-02-28"),
    (8, 26, "S72.001","Femoral Neck Fracture",              "acute",   "2024-02-28"),
    (8, 27, "I10",    "Essential Hypertension",            "chronic", "2024-06-15"),
    (8, 28, "F32.1",  "Major Depressive Disorder",         "chronic", "2024-10-08"),

    # Michael Johnson — cancer remission + diabetes
    (9, 29, "C34.12", "Lung Cancer (Right Upper Lobe)",    "chronic", "2024-03-20"),
    (9, 29, "E11.9",  "Type 2 Diabetes Mellitus",          "chronic", "2024-03-20"),
    (9, 30, "C34.12", "Lung Cancer in Remission",          "chronic", "2024-07-08"),
    (9, 31, "E11.9",  "Type 2 Diabetes Mellitus",          "chronic", "2024-11-05"),
]

# --------------------------------------------------------------------------
# Medications — (patient_index, name, dosage, start_date, end_date, is_active)
# --------------------------------------------------------------------------
MEDICATIONS = [
    # Margaret Collins
    ("Margaret Collins", "Metformin",    "500mg twice daily",  "2022-06-01", None,         1),
    ("Margaret Collins", "Furosemide",   "40mg daily",         "2023-01-10", None,         1),
    ("Margaret Collins", "Lisinopril",   "10mg daily",         "2021-03-15", None,         1),
    ("Margaret Collins", "Aspirin",      "81mg daily",         "2021-03-15", None,         1),
    ("Margaret Collins", "Atorvastatin", "40mg at night",      "2022-01-01", None,         1),

    # Robert Nguyen
    ("Robert Nguyen",    "Metoprolol",   "25mg twice daily",   "2023-02-14", None,         1),
    ("Robert Nguyen",    "Atorvastatin", "80mg at night",      "2023-02-14", None,         1),
    ("Robert Nguyen",    "Aspirin",      "81mg daily",         "2023-02-14", None,         1),
    ("Robert Nguyen",    "Lisinopril",   "20mg daily",         "2023-02-14", None,         1),

    # Linda Patel
    ("Linda Patel",      "Metformin",    "1000mg twice daily", "2021-05-01", None,         1),
    ("Linda Patel",      "Insulin Glargine","20 units nightly","2023-03-05", None,         1),
    ("Linda Patel",      "Amlodipine",   "5mg daily",          "2022-08-10", None,         1),
    ("Linda Patel",      "Erythropoietin","3000 IU weekly",    "2024-03-05", None,         1),

    # James Walker
    ("James Walker",     "Tiotropium",   "18mcg inhaled daily","2020-01-01", None,         1),
    ("James Walker",     "Furosemide",   "80mg twice daily",   "2020-06-01", None,         1),
    ("James Walker",     "Carvedilol",   "6.25mg twice daily", "2020-06-01", None,         1),
    ("James Walker",     "Warfarin",     "5mg daily",          "2021-01-01", None,         1),
    ("James Walker",     "Prednisone",   "10mg daily",         "2024-01-08", "2024-01-21", 0),
    ("James Walker",     "Oxygen therapy","2L/min continuous", "2023-06-01", None,         1),

    # Susan Martinez
    ("Susan Martinez",   "Albuterol inhaler","2 puffs as needed","2019-04-01",None,        1),
    ("Susan Martinez",   "Fluticasone",  "220mcg inhaled daily","2020-01-01",None,         1),
    ("Susan Martinez",   "Sertraline",   "50mg daily",         "2023-09-10", None,         1),

    # David Kim
    ("David Kim",        "Metformin",    "850mg twice daily",  "2022-03-01", None,         1),
    ("David Kim",        "Semaglutide",  "1mg weekly injection","2023-08-01",None,         1),
    ("David Kim",        "Atorvastatin", "40mg at night",      "2023-03-12", None,         1),

    # Barbara Thompson
    ("Barbara Thompson", "Warfarin",     "4mg daily",          "2024-02-01", None,         1),
    ("Barbara Thompson", "Metoprolol",   "50mg twice daily",   "2024-02-01", None,         1),
    ("Barbara Thompson", "Lisinopril",   "10mg daily",         "2024-02-01", None,         1),
    ("Barbara Thompson", "Clopidogrel",  "75mg daily",         "2024-02-01", None,         1),
    ("Barbara Thompson", "Atorvastatin", "80mg at night",      "2024-02-01", None,         1),

    # Charles Brown
    ("Charles Brown",    "Amoxicillin",  "500mg three times daily","2024-07-05","2024-07-12",0),

    # Patricia Davis
    ("Patricia Davis",   "Alendronate",  "70mg weekly",        "2022-02-28", None,         1),
    ("Patricia Davis",   "Calcium + D3", "1200mg/800IU daily", "2022-02-28", None,         1),
    ("Patricia Davis",   "Amlodipine",   "10mg daily",         "2023-06-15", None,         1),
    ("Patricia Davis",   "Sertraline",   "100mg daily",        "2024-10-08", None,         1),

    # Michael Johnson
    ("Michael Johnson",  "Metformin",    "500mg twice daily",  "2022-01-01", None,         1),
    ("Michael Johnson",  "Pembrolizumab","200mg IV q3 weeks",  "2023-03-20", "2024-09-20", 0),
    ("Michael Johnson",  "Ondansetron",  "8mg as needed",      "2023-03-20", "2024-09-20", 0),
    ("Michael Johnson",  "Dexamethasone","4mg daily",          "2023-03-20", "2024-01-01", 0),
]

# --------------------------------------------------------------------------
# Lab results — (patient_index, visit_index, test_name, value, unit,
#                reference_range, is_abnormal, test_date)
# --------------------------------------------------------------------------
LAB_RESULTS = [
    # Margaret Collins — visit 0 (Emergency, Cardiology)
    (0, 0,  "HbA1c",          8.9,  "%",       "4.0-5.6",     1, "2024-01-10"),
    (0, 0,  "BNP",            850,  "pg/mL",   "<100",        1, "2024-01-10"),
    (0, 0,  "Creatinine",     1.4,  "mg/dL",   "0.6-1.2",     1, "2024-01-10"),
    (0, 0,  "Sodium",         132,  "mEq/L",   "136-145",     1, "2024-01-10"),
    # Margaret Collins — visit 3 (Routine)
    (0, 3,  "HbA1c",          7.8,  "%",       "4.0-5.6",     1, "2024-09-18"),
    (0, 3,  "Fasting Glucose",162,  "mg/dL",   "70-99",       1, "2024-09-18"),

    # Robert Nguyen — visit 5
    (1, 5,  "Troponin I",     0.08, "ng/mL",   "<0.04",       1, "2024-02-14"),
    (1, 5,  "LDL Cholesterol",148,  "mg/dL",   "<100",        1, "2024-02-14"),
    (1, 5,  "HDL Cholesterol",38,   "mg/dL",   ">40",         1, "2024-02-14"),
    (1, 7,  "LDL Cholesterol",112,  "mg/dL",   "<100",        1, "2024-11-10"),
    (1, 7,  "Creatinine",     1.1,  "mg/dL",   "0.6-1.2",     0, "2024-11-10"),

    # Linda Patel — visit 8
    (2, 8,  "HbA1c",          9.2,  "%",       "4.0-5.6",     1, "2024-03-05"),
    (2, 8,  "eGFR",           38,   "mL/min",  ">60",         1, "2024-03-05"),
    (2, 8,  "Creatinine",     2.1,  "mg/dL",   "0.6-1.2",     1, "2024-03-05"),
    (2, 8,  "Potassium",      5.6,  "mEq/L",   "3.5-5.1",     1, "2024-03-05"),
    (2, 10, "eGFR",           35,   "mL/min",  ">60",         1, "2024-10-15"),
    (2, 10, "Creatinine",     2.3,  "mg/dL",   "0.6-1.2",     1, "2024-10-15"),

    # James Walker — visit 11 (very abnormal)
    (3, 11, "SpO2",           84,   "%",       "95-100",      1, "2024-01-08"),
    (3, 11, "FEV1",           32,   "% predicted",">=80",     1, "2024-01-08"),
    (3, 11, "BNP",            1240, "pg/mL",   "<100",        1, "2024-01-08"),
    (3, 11, "WBC",            14.2, "x10^9/L", "4.0-11.0",   1, "2024-01-08"),
    (3, 12, "Troponin I",     0.12, "ng/mL",   "<0.04",       1, "2024-02-20"),
    (3, 12, "BNP",            980,  "pg/mL",   "<100",        1, "2024-02-20"),
    (3, 16, "SpO2",           88,   "%",       "95-100",      1, "2024-11-30"),
    (3, 16, "WBC",            16.5, "x10^9/L", "4.0-11.0",   1, "2024-11-30"),

    # Susan Martinez — visit 17 (asthma attack)
    (4, 17, "SpO2",           91,   "%",       "95-100",      1, "2024-04-18"),
    (4, 17, "Peak Flow",      65,   "% predicted",">=80",     1, "2024-04-18"),
    (4, 18, "SpO2",           97,   "%",       "95-100",      0, "2024-09-10"),

    # David Kim — visit 20 (hyperglycemia episode)
    (5, 20, "Fasting Glucose",380,  "mg/dL",   "70-99",       1, "2024-08-05"),
    (5, 20, "HbA1c",          10.1, "%",       "4.0-5.6",     1, "2024-08-05"),
    (5, 21, "LDL Cholesterol",142,  "mg/dL",   "<100",        1, "2024-11-20"),
    (5, 21, "HbA1c",          8.4,  "%",       "4.0-5.6",     1, "2024-11-20"),

    # Barbara Thompson — visit 22 (stroke)
    (6, 22, "INR",            1.1,  "",        "2.0-3.0",     1, "2024-02-01"),
    (6, 22, "Platelet Count", 98,   "x10^9/L", "150-400",     1, "2024-02-01"),
    (6, 24, "INR",            2.4,  "",        "2.0-3.0",     0, "2024-10-22"),
    (6, 24, "BNP",            320,  "pg/mL",   "<100",        1, "2024-10-22"),

    # Charles Brown — visit 25 (appendicitis, otherwise healthy)
    (7, 25, "WBC",            14.8, "x10^9/L", "4.0-11.0",   1, "2024-07-04"),
    (7, 25, "CRP",            85,   "mg/L",    "<10",         1, "2024-07-04"),
    (7, 25, "Hemoglobin",     14.2, "g/dL",    "13.5-17.5",  0, "2024-07-04"),

    # Patricia Davis — visit 26 (hip fracture)
    (8, 26, "Hemoglobin",     9.8,  "g/dL",    "12.0-16.0",  1, "2024-02-28"),
    (8, 26, "Calcium",        8.1,  "mg/dL",   "8.5-10.5",   1, "2024-02-28"),
    (8, 27, "Hemoglobin",     11.2, "g/dL",    "12.0-16.0",  1, "2024-06-15"),
    (8, 28, "TSH",            3.2,  "mIU/L",   "0.4-4.0",    0, "2024-10-08"),

    # Michael Johnson — visit 29
    (9, 29, "CEA",            12.4, "ng/mL",   "<5.0",        1, "2024-03-20"),
    (9, 29, "HbA1c",          8.1,  "%",       "4.0-5.6",     1, "2024-03-20"),
    (9, 30, "CEA",            4.2,  "ng/mL",   "<5.0",        0, "2024-07-08"),
    (9, 31, "HbA1c",          7.6,  "%",       "4.0-5.6",     1, "2024-11-05"),
    (9, 31, "Fasting Glucose",148,  "mg/dL",   "70-99",       1, "2024-11-05"),
]


def seed():
    """Main function to insert all sample data into the database."""
    # Ensure tables exist
    create_tables()

    conn = get_connection()
    cursor = conn.cursor()

    # Clear existing data so we can re-run the script safely
    cursor.execute("DELETE FROM lab_results")
    cursor.execute("DELETE FROM medications")
    cursor.execute("DELETE FROM diagnoses")
    cursor.execute("DELETE FROM visits")
    cursor.execute("DELETE FROM patients")
    # Reset auto-increment counters
    cursor.execute("DELETE FROM sqlite_sequence")

    # ---------- Insert patients ----------
    cursor.executemany(
        "INSERT INTO patients (name, age, gender, blood_type, contact_number) VALUES (?,?,?,?,?)",
        PATIENTS
    )
    # Build a lookup: patient name -> patient_id (1-based index)
    patient_name_to_id = {name: i + 1 for i, (name, *_) in enumerate(PATIENTS)}

    # ---------- Insert visits ----------
    visit_rows = []
    for (p_idx, visit_date, discharge_date, visit_type, department, doctor) in VISITS:
        p_id = p_idx + 1  # patient IDs are 1-based
        visit_rows.append((p_id, visit_date, discharge_date, visit_type, department, doctor))

    cursor.executemany(
        "INSERT INTO visits (patient_id, visit_date, discharge_date, visit_type, department, attending_doctor) VALUES (?,?,?,?,?,?)",
        visit_rows
    )

    # ---------- Insert diagnoses ----------
    diag_rows = []
    for (p_idx, v_idx, code, name, dtype, date) in DIAGNOSES:
        diag_rows.append((p_idx + 1, v_idx + 1, code, name, dtype, date))

    cursor.executemany(
        "INSERT INTO diagnoses (patient_id, visit_id, diagnosis_code, diagnosis_name, diagnosis_type, diagnosed_date) VALUES (?,?,?,?,?,?)",
        diag_rows
    )

    # ---------- Insert medications ----------
    med_rows = []
    for (p_name, med_name, dosage, start, end, active) in MEDICATIONS:
        p_id = patient_name_to_id[p_name]
        med_rows.append((p_id, med_name, dosage, start, end, active))

    cursor.executemany(
        "INSERT INTO medications (patient_id, medication_name, dosage, start_date, end_date, is_active) VALUES (?,?,?,?,?,?)",
        med_rows
    )

    # ---------- Insert lab results ----------
    lab_rows = []
    for (p_idx, v_idx, test, value, unit, ref, abnormal, date) in LAB_RESULTS:
        lab_rows.append((p_idx + 1, v_idx + 1, test, value, unit, ref, abnormal, date))

    cursor.executemany(
        "INSERT INTO lab_results (patient_id, visit_id, test_name, result_value, unit, reference_range, is_abnormal, test_date) VALUES (?,?,?,?,?,?,?,?)",
        lab_rows
    )

    conn.commit()
    conn.close()

    # Quick verification print
    conn2 = get_connection()
    cur2 = conn2.cursor()
    print("=== Seed complete. Row counts ===")
    for table in ["patients", "visits", "diagnoses", "medications", "lab_results"]:
        cur2.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur2.fetchone()[0]
        print(f"  {table:15s}: {count} rows")
    conn2.close()


if __name__ == "__main__":
    seed()

