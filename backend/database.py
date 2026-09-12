"""
database.py
-----------
SQLite setup for the OIL SIF/NLP reports database.

Schema mirrors exactly what both frontend dashboards already send/expect
(see worker-portal/script.js buildReportPayload() and
hsse-console/script.js's rendering code).
"""

import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / "reports.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS reports (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id          TEXT,
    site               TEXT,
    activity           TEXT,
    location           TEXT,
    report_type        TEXT,
    description        TEXT NOT NULL,
    weather            TEXT,
    equipment          TEXT,
    ppe_compliant      INTEGER,
    submitted_at       TEXT NOT NULL,
    sif_potential      INTEGER,      -- 0 / 1 / NULL (NULL = not yet classified)
    confidence         REAL,
    rule_tag           TEXT,
    precursor_keywords TEXT,         -- stored as a JSON string, e.g. '["confined space"]'
    status             TEXT NOT NULL DEFAULT 'pending'
);
"""


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(SCHEMA)
    conn.commit()
    conn.close()


def row_to_dict(row: sqlite3.Row) -> dict:
    """Convert a DB row into the JSON shape the frontend expects."""
    d = dict(row)
    d["ppe_compliant"] = bool(d["ppe_compliant"]) if d["ppe_compliant"] is not None else None
    d["sif_potential"] = bool(d["sif_potential"]) if d["sif_potential"] is not None else None
    d["precursor_keywords"] = json.loads(d["precursor_keywords"]) if d["precursor_keywords"] else []
    return d