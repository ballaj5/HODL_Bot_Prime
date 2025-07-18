# src/utils/db.py
import sqlite3
import threading
import logging
import json
from .paths import get_path

logger = logging.getLogger(__name__)
DB_FILE = get_path("signals.db")
thread_local = threading.local()

def get_db_conn():
    if not hasattr(thread_local, 'conn'):
        thread_local.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    return thread_local.conn

def init_db():
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id TEXT PRIMARY KEY,
            signal_data TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    logger.info("Database initialized.")

def store_signal(signal_id: str, data: dict):
    from datetime import datetime
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        # Serialize the dictionary to a JSON string for storage
        json_data = json.dumps(data)
        cursor.execute("""
            INSERT INTO signals (id, signal_data, timestamp) VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET signal_data=excluded.signal_data, timestamp=excluded.timestamp
        """, (signal_id, json_data, datetime.utcnow().isoformat()))
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Failed to store signal {signal_id}: {e}")
        conn.rollback()

def load_all_signals() -> list:
    """Loads all signals from the database from the latest run."""
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, signal_data FROM signals")
        rows = cursor.fetchall()
        signals = []
        for row_id, json_data in rows:
            symbol, timeframe = row_id.split('-')
            data = json.loads(json_data)
            signals.append({
                "symbol": symbol,
                "timeframe": timeframe,
                **data
            })
        return signals
    except sqlite3.Error as e:
        logger.error(f"Failed to load all signals: {e}")
        return []