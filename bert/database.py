import sqlite3
from datetime import datetime, timedelta
import json

DB_PATH = "sensitive_data.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Updated schema INCLUDING reformulated_message
    c.execute("""
    CREATE TABLE IF NOT EXISTS sensitive_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        raw_message TEXT,
        sanitized_message TEXT,
        reformulated_message TEXT,
        topic TEXT,
        notices TEXT,
        stored_at TEXT,
        expires_at TEXT,
        retention_policy TEXT
    )
    """)

    # BACKWARD SAFETY:
    # If DB already exists, ensure reformulated_message column exists
    try:
        c.execute("ALTER TABLE sensitive_data ADD COLUMN reformulated_message TEXT;")
    except:
        pass  # column already exists

    conn.commit()
    conn.close()


def save_sensitive_message(
    raw=None,
    sanitized=None,
    reformulated=None,
    topic=None,
    notices=None,
    retention="30d"
):
    """
    Saves EXACTLY ONE of:
      - raw_message
      - sanitized_message
      - reformulated_message
    """

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    now = datetime.utcnow()
    expires = now + parse_retention(retention)

    # Ensure notices always stored as JSON list
    if isinstance(notices, list):
        notices = json.dumps(notices)
    elif notices is None:
        notices = json.dumps([])
    else:
        try:
            json.loads(notices)
        except:
            notices = json.dumps([])

    c.execute("""
        INSERT INTO sensitive_data 
        (raw_message, sanitized_message, reformulated_message, topic, notices, stored_at, expires_at, retention_policy)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        raw,
        sanitized,
        reformulated,
        topic,
        notices,
        now.isoformat(),
        expires.isoformat(),
        retention
    ))

    conn.commit()
    conn.close()


def parse_retention(retention):
    """
    Accepts "120", "120d", or "1y".
    Enforces max 365 days and min 1 day.
    """
    # simple number
    if retention.isdigit():
        days = max(1, min(int(retention), 365))
        return timedelta(days=days)

    # "Xd"
    if retention.endswith("d"):
        days = max(1, min(int(retention[:-1]), 365))
        return timedelta(days=days)

    # "Xy"
    if retention.endswith("y"):
        years = int(retention[:-1])
        return timedelta(days=min(years * 365, 365))

    # fallback default
    return timedelta(days=30)
