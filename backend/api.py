from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta
import sys
import os
import json
import re

# Fix Python path so we can import bert package
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)

from bert.integrated_sanitizer import sanitize as run_sanitizer

app = Flask(__name__)
CORS(app)

DB_PATH = "sensitive_data.db"

##########################################
# Initialize DB
##########################################

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Updated schema INCLUDING reformulated_message
    cur.execute("""
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

    # Add column if DB already existed
    try:
        cur.execute("ALTER TABLE sensitive_data ADD COLUMN gdpr_categories TEXT;")
    except:
        pass

    try:
        cur.execute("ALTER TABLE sensitive_data ADD COLUMN risk_assessment TEXT;")
    except:
        pass

    conn.commit()
    conn.close()


##########################################
# Retention Helpers
##########################################

def parse_retention(retention):
    """
    Accepts "120", "120d", or "1y".
    Enforces max 365 days and min 1 day.
    """
    if not retention:
        return timedelta(days=30)

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


def normalize_retention(value):
    if not value:
        return "30d"

    value = value.strip()

    if value.endswith(" days"):
        num = value.replace(" days", "").strip()
        return f"{num}d"

    if value == "1 year":
        return "365d"

    return value


##########################################
# Save Message (raw, sanitized OR reformulated)
##########################################

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
    now = datetime.utcnow()
    expires = now + parse_retention(retention)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    notices = json.dumps(notices or [])
    gdpr_categories = json.dumps(gdpr_categories or [])
    risk_assessment = json.dumps(risk_assessment or {})
    cur.execute("""
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
    conn.close()


##########################################
# Fetch Dashboard Data
##########################################

def fetch_all():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT * FROM sensitive_data ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()

    results = []
    for row in rows:
        results.append({
            "id": row[0],
            "original": row[1],
            "sanitized": row[2],
            "reformulated": row[3],
            "topic": row[4],
            "notices": json.loads(row[5] or "[]"),
            "gdpr_categories": json.loads(row[6] or "[]"),
            "risk_assessment": json.loads(row[7] or "{}"),
            "created_at": row[8],
            "expires_at": row[9],
            "retention": normalize_retention(row[10])
        })

    return results


@app.route("/api/data", methods=["GET"])
def get_data():
    return jsonify(fetch_all())


##########################################
# SANITIZE — NOW includes position tracking
##########################################

@app.route("/api/sanitize", methods=["POST"])
def sanitize_handler():
    data = request.get_json(force=True, silent=True) or {}
    text = data.get("text", "")

    result = run_sanitizer(text)

    detected_items = []
    used_positions = set()

    for n in result["notices"]:
        detected_text = n["text"]

        # find first unused occurrence in original text
        for match in re.finditer(re.escape(detected_text), text):
            start = match.start()

            if start in used_positions:
                continue

            used_positions.add(start)

            detected_items.append({
                "id": f"item_{len(detected_items)}",
                "type": n["type"],
                "text": detected_text,
                "start": start,
                "end": match.end(),
                "mask": f"[{n['type']}_REMOVED]"
            })

            break  # only one match per notice

    return jsonify({
        "original": text,
        "sanitized": result["sanitized"],
        "detected": detected_items,
        "topic": result["topic"],
        "gdpr_categories": result.get("gdpr_categories", []),
        "risk_assessment": result.get("risk_assessment", {})
    })


##########################################
# APPLY MASKING
##########################################

@app.post("/api/apply_mask")
def apply_mask():
    data = request.get_json(force=True, silent=True) or {}
    original = data.get("text", "")
    choices = data.get("choices", {})
    detected = data.get("detected", [])

    final_text = original

    detected_sorted = sorted(detected, key=lambda x: x["start"], reverse=True)

    for item in detected_sorted:
        if choices.get(item["id"]) == "remove":
            start = item["start"]
            end = item["end"]
            final_text = final_text[:start] + item["mask"] + final_text[end:]

    return jsonify({"final_text": final_text})


##########################################
# SAVE Original
##########################################

@app.post("/api/save_original")
def save_original():
    data = request.get_json(force=True, silent=True) or {}

    save_sensitive_message(
        raw=data.get("original"),
        sanitized=None,
        reformulated=None,
        topic=data.get("topic"),
        notices=[],
        retention=data.get("retention")
    )

    return {"status": "saved_original"}


##########################################
# SAVE Sanitized
##########################################

@app.post("/api/save_sanitized")
def save_sanitized():
    data = request.get_json(force=True, silent=True) or {}

    save_sensitive_message(
        raw=None,
        sanitized=data.get("sanitized"),
        reformulated=None,
        topic=data.get("topic"),
        notices=data.get("detected", []),
        gdpr_categories=data.get("gdpr_categories", []),
        risk_assessment=data.get("risk_assessment", {}),
        retention=data.get("retention")
    )

    return {"status": "saved_sanitized"}


##########################################
# REFORMULATE PROMPT
##########################################

@app.post("/api/reformulate")
def reformulate_endpoint():
    from reformulator import reformulate

    data = request.get_json(force=True, silent=True) or {}
    sanitized = data.get("sanitized", "")
    kept_items = data.get("kept_items", [])

    result = reformulate(sanitized, kept_items)

    return jsonify({"reformulated": result})


##########################################
# SAVE Reformulated Prompt
##########################################

@app.post("/api/save_reformulated")
def save_reformulated():
    data = request.get_json(force=True, silent=True) or {}

    save_sensitive_message(
        raw=None,
        sanitized=None,
        reformulated=data.get("reformulated"),
        topic=data.get("topic"),
        notices=data.get("detected", []),
        gdpr_categories=data.get("gdpr_categories", []),
        risk_assessment=data.get("risk_assessment", {}),
        retention=data.get("retention")
    )
    return {"status": "saved_reformulated"}


##########################################
# DELETE & RETENTION UPDATE
##########################################

@app.route("/api/update/<int:entry_id>", methods=["PUT"])
def update_retention(entry_id):
    data = request.get_json(force=True, silent=True) or {}
    retention = normalize_retention(data.get("retention"))
    new_expires = (datetime.utcnow() + parse_retention(retention)).isoformat()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        UPDATE sensitive_data
        SET retention_policy = ?, expires_at = ?
        WHERE id = ?
    """, (retention, new_expires, entry_id))

    conn.commit()
    conn.close()

    return {"status": "updated", "retention": retention, "expires_at": new_expires}


@app.route("/api/delete/<int:entry_id>", methods=["DELETE"])
def delete_entry(entry_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("DELETE FROM sensitive_data WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()

    return {"status": "deleted"}


@app.post("/api/delete_bulk")
def delete_bulk():
    data = request.get_json(force=True, silent=True) or {}
    ids = data.get("ids", [])

    if not ids:
        return {"status": "bulk_deleted", "count": 0}

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    query = f"DELETE FROM sensitive_data WHERE id IN ({','.join('?' * len(ids))})"
    cur.execute(query, ids)

    conn.commit()
    conn.close()

    return {"status": "bulk_deleted", "count": len(ids)}

##########################################
# START API
##########################################

if __name__ == "__main__":
    init_db()
    app.run(port=5000, debug=True)
