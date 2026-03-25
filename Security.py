from transformers import pipeline
from datetime import datetime
from huggingface_hub import login
import sqlite3
from dotenv import load_dotenv
import os
load_dotenv(r"ResearchAssistant/GOOGLE_API_KEY.env")

# ─────────────────────────────────────────────
# DATABASE SETUP
# ─────────────────────────────────────────────
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "security.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ip_violations (
            ip_address      TEXT PRIMARY KEY,
            violation_count INTEGER DEFAULT 0,
            blacklisted     BOOLEAN DEFAULT FALSE,
            last_violation  TEXT
        )
    """)
    conn.commit()
    conn.close()

# ─────────────────────────────────────────────
# IN-MEMORY TRACKING (current session counts)
# ─────────────────────────────────────────────
IP_VIOLATIONS = {}  # resets on restart — just for current session counting

# ─────────────────────────────────────────────
# HUGGINGFACE GUARD MODEL
# ─────────────────────────────────────────────
guard = pipeline("text-classification", model="unitary/toxic-bert")

def is_harmful(user_input: str) -> bool:
    result = guard(user_input)[0]
    
    label = result["label"]
    score = result["score"]

    print(f"Security check — label: {label}, confidence: {score:.2f}")

    if label == "toxic" and score > 0.90:
        print(f"BLOCKED — toxic content detected at {score:.2f} confidence")
        return True
        
    return False

# ─────────────────────────────────────────────
# IP BLACKLIST FUNCTIONS
# ─────────────────────────────────────────────
def is_blacklisted(ip: str) -> bool:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT blacklisted FROM ip_violations WHERE ip_address = ?", (ip,)
    )
    row = cursor.fetchone()
    conn.close()
    return bool(row and row[0])

def record_violation(ip: str):
    # Track in memory for current session
    IP_VIOLATIONS[ip] = IP_VIOLATIONS.get(ip, 0) + 1

    # Persist to SQLite
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Insert or update violation record
    cursor.execute("""
        INSERT INTO ip_violations (ip_address, violation_count, blacklisted, last_violation)
        VALUES (?, 1, FALSE, ?)
        ON CONFLICT(ip_address) DO UPDATE SET
            violation_count = violation_count + 1,
            last_violation = ?
    """, (ip, datetime.now().isoformat(), datetime.now().isoformat()))

    # Blacklist if total violations exceed 3
    cursor.execute("""
        UPDATE ip_violations
        SET blacklisted = TRUE
        WHERE ip_address = ? AND violation_count > 3
    """, (ip,))

    conn.commit()
    conn.close()

    if IP_VIOLATIONS[ip] > 3:
        print(f"IP {ip} has been blacklisted.")

# Initialize database on import
init_db()

#security testing
if __name__ == "__main__":
    print(is_blacklisted("192.168.1.1"))      # should print False
    record_violation("192.168.1.2")
    record_violation("192.168.1.2")
    record_violation("192.168.1.2")
    record_violation("192.168.1.2")
    print(is_blacklisted("192.168.1.3"))      # should now print True
