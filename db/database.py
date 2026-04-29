import sqlite3
import json

DB_PATH = "data.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id              TEXT PRIMARY KEY,
                name            TEXT,
                symptoms        TEXT,
                severity        TEXT,
                result          TEXT,
                pdf_data        BLOB,
                medical_history TEXT DEFAULT '',
                allergies       TEXT DEFAULT '',
                created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Add columns if upgrading from old schema
        try:
            conn.execute("ALTER TABLE reports ADD COLUMN medical_history TEXT DEFAULT ''")
        except Exception:
            pass
        try:
            conn.execute("ALTER TABLE reports ADD COLUMN allergies TEXT DEFAULT ''")
        except Exception:
            pass
        conn.commit()

def save_report(report_id: str, name: str, symptoms: str, severity: str,
                result: str, medical_history: str = "", allergies: str = ""):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO reports
               (id, name, symptoms, severity, result, medical_history, allergies)
               VALUES (?,?,?,?,?,?,?)""",
            (report_id, name, symptoms, severity, result, medical_history, allergies),
        )
        conn.commit()

def get_all():
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM reports ORDER BY created_at DESC"
        ).fetchall()

def get_by_id(report_id: str):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM reports WHERE id=?", (report_id,)
        ).fetchone()

def get_dashboard_stats():
    with get_conn() as conn:
        rows = conn.execute("SELECT result, severity, created_at, symptoms FROM reports").fetchall()

    condition_count = {}
    severity_count  = {"high": 0, "medium": 0, "mild": 0}
    monthly_count   = {}
    daily_count     = {}
    all_conditions  = []

    for result_json, severity, created_at, symptoms in rows:
        # severity
        sev = severity or "medium"
        severity_count[sev] = severity_count.get(sev, 0) + 1

        # monthly & daily
        if created_at:
            month = created_at[:7]           # YYYY-MM
            day   = created_at[:10]          # YYYY-MM-DD
            monthly_count[month] = monthly_count.get(month, 0) + 1
            daily_count[day]     = daily_count.get(day, 0) + 1

        # conditions
        try:
            r = json.loads(result_json)
            for c in r.get("possible_conditions", []):
                condition_count[c] = condition_count.get(c, 0) + 1
                all_conditions.append(c)
        except Exception:
            pass

    total = len(rows)
    top_conditions = sorted(condition_count.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "total_reports":    total,
        "severity_count":   severity_count,
        "top_conditions":   top_conditions,
        "monthly_trend":    sorted(monthly_count.items()),
        "daily_trend":      sorted(daily_count.items())[-30:],
        "condition_count":  condition_count,
    }
