import sqlite3
from datetime import datetime, timedelta
import json

DB_PATH = "sensitive_data.db"


# ============================================================
# Initialize DB
# ============================================================

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()

        c.execute("""
        CREATE TABLE IF NOT EXISTS sensitive_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_message TEXT,
            sanitized_message TEXT,
            reformulated_message TEXT,
            topic TEXT,
            notices TEXT,
            gdpr_categories TEXT,
            risk_assessment TEXT,
            stored_at TEXT,
            expires_at TEXT,
            retention_policy TEXT
        )
        """)

        # Backward compatibility safety
        try:
            c.execute("ALTER TABLE sensitive_data ADD COLUMN gdpr_categories TEXT;")
        except:
            pass

        try:
            c.execute("ALTER TABLE sensitive_data ADD COLUMN risk_assessment TEXT;")
        except:
            pass
# ============================================================
# Fetch All Records
# ============================================================

def fetch_all():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM sensitive_data ORDER BY id DESC")
        rows = c.fetchall()

    results = []

    for row in rows:
        results.append({
            "id": row[0],
            "raw_message": row[1],
            "sanitized_message": row[2],
            "reformulated_message": row[3],
            "topic": row[4],
            "notices": json.loads(row[5] or "[]"),
            "gdpr_categories": json.loads(row[6] or "[]"),
            "risk_assessment": json.loads(row[7] or "{}"),
            "stored_at": row[8],
            "expires_at": row[9],
            "retention_policy": row[10],
        })

    return results
# ============================================================
# Retention Parser
# ============================================================

def parse_retention(retention):
    """
    Accepts:
        "30"   -> 30 days
        "30d"  -> 30 days
        "1y"   -> 365 days
    Enforces min 1 day, max 365 days.
    """

    if not retention:
        return timedelta(days=30)

    retention = str(retention).strip()

    if retention.isdigit():
        days = max(1, min(int(retention), 365))
        return timedelta(days=days)

    if retention.endswith("d"):
        days = max(1, min(int(retention[:-1]), 365))
        return timedelta(days=days)

    if retention.endswith("y"):
        years = int(retention[:-1])
        return timedelta(days=min(years * 365, 365))

    return timedelta(days=30)
# ============================================================
# Save Message
# ============================================================

def save_sensitive_message(
    raw=None,
    sanitized=None,
    reformulated=None,
    topic=None,
    notices=None,
    gdpr_categories=None,
    risk_assessment=None,
    retention="30d"
):
    """
    Stores exactly one of:
      - raw_message
      - sanitized_message
      - reformulated_message
    """
    message_fields = [raw, sanitized, reformulated]
    if sum(bool(x) for x in message_fields) != 1:
        raise ValueError(
            "Exactly one of raw, sanitized, or reformulated must be provided."
        )
    now = datetime.utcnow()
    expires = now + parse_retention(retention)

    notices = json.dumps(notices or [])
    gdpr_categories = json.dumps(gdpr_categories or [])
    risk_assessment = json.dumps(risk_assessment or {})

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()

        c.execute("""
            INSERT INTO sensitive_data
            (
                raw_message,
                sanitized_message,
                reformulated_message,
                topic,
                notices,
                gdpr_categories,
                risk_assessment,
                stored_at,
                expires_at,
                retention_policy
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            raw,
            sanitized,
            reformulated,
            topic,
            notices,
            gdpr_categories,
            risk_assessment,
            now.isoformat(),
            expires.isoformat(),
            retention
        ))

        conn.commit()   